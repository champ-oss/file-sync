"""Provides tests for GitHub utility."""
import unittest
from unittest.mock import MagicMock

from github import UnknownObjectException, GithubException
from typing_extensions import Self

from config_util.file_config import FileConfig
from github_util.github_util import GitHubUtil


class TestGitHubUtil(unittest.TestCase):
    """Provides tests for GitHub utility."""

    def setUp(self: Self) -> None:
        """Set up the requirements for testing."""
        self.github_session = MagicMock()
        self.github_util = GitHubUtil(access_token='test123', github_session=self.github_session)

    def test_get_repo(self: Self) -> None:
        """Validate the get_repo function is successful."""
        self.assertIsNotNone(self.github_util.get_repo(repo_name='my-org/test-repo-1'))

        self.github_session.get_repo.side_effect = UnknownObjectException(400)
        self.assertIsNone(self.github_util.get_repo(repo_name='my-org/test-repo-1'))

        self.github_session.get_repo.side_effect = GithubException(status=422, message='Not found')
        self.assertIsNone(self.github_util.get_repo(repo_name='my-org/test-repo-1'))

    def test_create_branch_if_not_exists_with_not_found_exception(self: Self) -> None:
        """Validate the create_branch_if_not_exists function is successful."""
        repo = MagicMock()
        branch = MagicMock()
        branch.commit.sha = '123'

        repo.get_branch.side_effect = [
            GithubException(status=404, data={'message': 'Branch not found'}),
            branch
        ]
        self.github_util.create_branch_if_not_exists(repo=repo, branch_name='test-branch')
        repo.create_git_ref.assert_called_once()
        repo.create_git_ref.assert_called_with(ref='refs/heads/test-branch', sha='123')

    def test_create_branch_if_not_exists_with_branch_already_exists(self: Self) -> None:
        """Validate the create_branch_if_not_exists function is successful."""
        repo = MagicMock()
        repo.get_branch.return_value = 'test-branch'
        self.github_util.create_branch_if_not_exists(repo=repo, branch_name='test-branch')
        repo.create_git_ref.assert_not_called()

    def test_is_file_up_to_date_should_return_true(self: Self) -> None:
        """Validate the is_file_up_to_date function is successful."""
        source_file = FileConfig(source_path='', destination_path='foo', sha='123')
        destination_repo = MagicMock()
        destination_repo.get_contents.return_value.sha = '123'
        self.assertTrue(self.github_util.is_file_up_to_date(source_file, destination_repo, branch='main'))
        destination_repo.get_contents.assert_called_with('foo', ref='main')

    def test_is_file_up_to_date_should_return_false(self: Self) -> None:
        """Validate the is_file_up_to_date function is successful."""
        source_file = FileConfig(source_path='', destination_path='foo', sha='123')
        destination_repo = MagicMock()
        destination_repo.get_contents.return_value.sha = '456'
        self.assertFalse(self.github_util.is_file_up_to_date(source_file, destination_repo, branch='main'))
        destination_repo.get_contents.assert_called_with('foo', ref='main')

    def test_is_file_up_to_date_should_return_false_when_file_not_found(self: Self) -> None:
        """Validate the is_file_up_to_date function is successful."""
        destination_repo = MagicMock()
        destination_repo.get_contents.side_effect = UnknownObjectException(404)
        self.assertFalse(self.github_util.is_file_up_to_date(MagicMock(), destination_repo, branch='main'))

        destination_repo = MagicMock()
        destination_repo.get_contents.side_effect = GithubException(status=404, data={'message': 'File not found'}),
        self.assertFalse(self.github_util.is_file_up_to_date(MagicMock(), destination_repo, branch='main'))

    def test_update_file_should_update_existing_file(self: Self) -> None:
        """Validate the update_file function is successful."""
        source_file = FileConfig(source_path='', destination_path='foo', content=b'foo')
        destination_repo = MagicMock()
        destination_repo.get_contents.return_value.sha = '456'
        self.github_util.update_file(destination_repo, source_file, branch='main')
        destination_repo.update_file.assert_called_once()
        destination_repo.update_file.assert_called_with(
            path='foo', message='Updated by file-sync', content=b'foo', sha='456', branch='main'
        )

    def test_update_file_should_create_a_new_file(self: Self) -> None:
        """Validate the update_file function is successful."""
        source_file = FileConfig(source_path='', destination_path='foo', content=b'foo')
        destination_repo = MagicMock()
        destination_repo.get_contents.side_effect = UnknownObjectException(404)
        self.github_util.update_file(destination_repo, source_file, branch='main')
        destination_repo.create_file.assert_called_once()
        destination_repo.create_file.assert_called_with(
            path='foo', message='Updated by file-sync', content=b'foo', branch='main'
        )

    def test_create_pull_request(self: Self) -> None:
        """Validate the create_pull_request function is successful."""
        repo = MagicMock()
        self.github_util.create_pull_request(repo, 'test-branch')
        repo.create_pull.assert_called_once()
        repo.create_pull.assert_called_with(
            title='file-sync', head='test-branch', base='main'
        )

        repo = MagicMock()
        repo.create_pull.side_effect = GithubException(status=422, data={'message': 'Invalid request'})
        self.github_util.create_pull_request(repo, 'test-branch')
        repo.create_pull.assert_called_once()
        repo.create_pull.assert_called_with(
            title='file-sync', head='test-branch', base='main'
        )

    def test_get_sync_files_from_source_repo(self: Self) -> None:
        """Validate the get_sync_files_from_source_repo function is successful."""
        template_file = MagicMock()
        template_file.sha = '123'
        template_file.content = 'Zm9vCg=='

        source_repo = MagicMock()
        source_repo.get_contents.return_value = template_file
        self.github_session.get_repo.return_value = source_repo

        sync_files = self.github_util.get_sync_files_from_source_repo(
            source_repo_name='my-org/test-repo-1', action_input_files='foo/bar.yml', source_branch='main'
        )
        expected = [FileConfig(source_path='foo/bar.yml', destination_path='foo/bar.yml', content=b'foo\n', sha='123')]
        self.assertEqual(expected, sync_files)

        self.github_session.get_repo.assert_called_once()
        self.github_session.get_repo.assert_called_with('my-org/test-repo-1')

        source_repo.get_contents.assert_called_once()
        source_repo.get_contents.assert_called_with('foo/bar.yml', ref='main')
