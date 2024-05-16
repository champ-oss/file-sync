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
        self.github_util = GitHubUtil(access_token='test123', repository_name='test-repository',
                                      github_session=self.github_session)

    def test_get_repo(self: Self) -> None:
        """Validate the get_repo function is successful."""
        self.assertIsNotNone(self.github_util._get_repo(MagicMock(), 'my-org/test-repo-1'))

        github_session = MagicMock()
        github_session.get_repo.side_effect = UnknownObjectException(400)
        self.assertIsNone(self.github_util._get_repo(github_session, 'my-org/test-repo-1'))

        github_session = MagicMock()
        github_session.get_repo.side_effect = GithubException(status=422, message='Not found')
        self.assertIsNone(self.github_util._get_repo(github_session, 'my-org/test-repo-1'))

    def test_create_branch_if_not_exists_with_not_found_exception(self: Self) -> None:
        """Validate the create_branch_if_not_exists function is successful."""
        self.github_util.repository = MagicMock()
        branch = MagicMock()
        branch.commit.sha = '123'

        self.github_util.repository.get_branch.side_effect = [
            GithubException(status=404, data={'message': 'Branch not found'}),
            branch
        ]
        self.github_util._create_branch_if_not_exists(branch_name='test-branch')
        self.github_util.repository.create_git_ref.assert_called_once()
        self.github_util.repository.create_git_ref.assert_called_with(ref='refs/heads/test-branch', sha='123')

    def test_create_branch_if_not_exists_with_branch_already_exists(self: Self) -> None:
        """Validate the create_branch_if_not_exists function is successful."""
        self.github_util.repository = MagicMock()
        self.github_util.repository.get_branch.return_value = 'test-branch'
        self.github_util._create_branch_if_not_exists(branch_name='test-branch')
        self.github_util.repository.create_git_ref.assert_not_called()

    def test_is_file_up_to_date_should_return_true(self: Self) -> None:
        """Validate the is_file_up_to_date function is successful."""
        source_file = FileConfig(source_path='', destination_path='foo', sha='123')
        self.github_util.repository = MagicMock()
        self.github_util.repository.get_contents.return_value.sha = '123'
        self.assertTrue(self.github_util._is_file_up_to_date(source_file, branch='main'))
        self.github_util.repository.get_contents.assert_called_with('foo', ref='main')

    def test_is_file_up_to_date_should_return_false(self: Self) -> None:
        """Validate the is_file_up_to_date function is successful."""
        source_file = FileConfig(source_path='', destination_path='foo', sha='123')
        self.github_util.repository = MagicMock()
        self.github_util.repository.get_contents.return_value.sha = '456'
        self.assertFalse(self.github_util._is_file_up_to_date(source_file, branch='main'))
        self.github_util.repository.get_contents.assert_called_with('foo', ref='main')

    def test_is_file_up_to_date_should_return_false_when_file_not_found(self: Self) -> None:
        """Validate the is_file_up_to_date function is successful."""
        self.github_util.repository = MagicMock()
        self.github_util.repository.get_contents.side_effect = UnknownObjectException(404)
        self.assertFalse(self.github_util._is_file_up_to_date(MagicMock(), branch='main'))

        self.github_util.repository = MagicMock()
        self.github_util.repository.get_contents.side_effect = GithubException(status=404,
                                                                               data={'message': 'File not found'}),
        self.assertFalse(self.github_util._is_file_up_to_date(MagicMock(), branch='main'))

    def test_update_file_should_update_existing_file(self: Self) -> None:
        """Validate the update_file function is successful."""
        source_file = FileConfig(source_path='', destination_path='foo', content=b'foo')
        self.github_util.repository = MagicMock()
        self.github_util.repository.get_contents.return_value.sha = '456'
        self.github_util._update_file(source_file, branch='main')
        self.github_util.repository.update_file.assert_called_once()
        self.github_util.repository.update_file.assert_called_with(
            path='foo', message='Updated by file-sync', content=b'foo', sha='456', branch='main'
        )

    def test_update_file_should_create_a_new_file(self: Self) -> None:
        """Validate the update_file function is successful."""
        source_file = FileConfig(source_path='', destination_path='foo', content=b'foo')
        self.github_util.repository = MagicMock()
        self.github_util.repository.get_contents.side_effect = UnknownObjectException(404)
        self.github_util._update_file(source_file, branch='main')
        self.github_util.repository.create_file.assert_called_once()
        self.github_util.repository.create_file.assert_called_with(
            path='foo', message='Updated by file-sync', content=b'foo', branch='main'
        )

    def test_create_pull_request(self: Self) -> None:
        """Validate the create_pull_request function is successful."""
        self.github_util.repository = MagicMock()
        self.github_util.create_pull_request('test-branch')
        self.github_util.repository.create_pull.assert_called_once()
        self.github_util.repository.create_pull.assert_called_with(
            title='file-sync', head='test-branch', base='main', draft=False
        )

        self.github_util.repository = MagicMock()
        self.github_util.repository.create_pull.side_effect = GithubException(status=422,
                                                                              data={'message': 'Invalid request'})
        self.github_util.create_pull_request('test-branch')
        self.github_util.repository.create_pull.assert_called_once()
        self.github_util.repository.create_pull.assert_called_with(
            title='file-sync', head='test-branch', base='main', draft=False
        )

    def test_get_sync_files_from_source_repo(self: Self) -> None:
        """Validate the get_sync_files_from_source_repo function is successful."""
        template_file = MagicMock()
        template_file.sha = '123'
        template_file.content = 'Zm9vCg=='

        self.github_util.repository = MagicMock()
        self.github_util.repository.get_contents.return_value = template_file

        sync_files = self.github_util.get_sync_files_from_source_repo(action_input_files='foo/bar.yml', branch='main')
        expected = [FileConfig(source_path='foo/bar.yml', destination_path='foo/bar.yml', content=b'foo\n', sha='123')]
        self.assertEqual(expected, sync_files)

        self.github_util.repository.get_contents.assert_called_once()
        self.github_util.repository.get_contents.assert_called_with('foo/bar.yml', ref='main')

    def test_sync_files_for_repo_when_already_up_to_date_on_main_branch(self: Self) -> None:
        """Validate the sync_files_for_repo function is successful."""
        self.github_util.repository = MagicMock()
        self.github_util._is_file_up_to_date = MagicMock()
        self.github_util._is_file_up_to_date.side_effect = [
            True  # file is up-to-date on main branch
        ]
        self.github_util._create_branch_if_not_exists = MagicMock()
        self.github_util._update_file = MagicMock()

        self.github_util.sync_files_for_repo(
            [FileConfig(source_path='foo/bar.yml', destination_path='foo/bar.yml', content=b'foo\n', sha='123')]
        )
        self.github_util._is_file_up_to_date.assert_called_once()
        self.github_util._create_branch_if_not_exists.assert_not_called()
        self.github_util._update_file.assert_not_called()

    def test_sync_files_for_repo_when_already_up_to_date_on_file_sync_branch(self: Self) -> None:
        """Validate the sync_files_for_repo function is successful."""
        self.github_util.repository = MagicMock()
        self.github_util._is_file_up_to_date = MagicMock()
        self.github_util._is_file_up_to_date.side_effect = [
            False,  # file is not up-to-date on main branch
            True  # file is up-to-date on file-sync branch
        ]
        self.github_util._create_branch_if_not_exists = MagicMock()
        self.github_util._update_file = MagicMock()

        self.github_util.sync_files_for_repo(
            [FileConfig(source_path='foo/bar.yml', destination_path='foo/bar.yml', content=b'foo\n', sha='123')]
        )
        self.github_util._create_branch_if_not_exists.assert_called_once()
        self.github_util._create_branch_if_not_exists.assert_called_with('file-sync')
        self.github_util._update_file.assert_not_called()

    def test_sync_files_for_repo_when_not_up_to_date(self: Self) -> None:
        """Validate the sync_files_for_repo function is successful."""
        self.github_util.repository = MagicMock()
        self.github_util._is_file_up_to_date = MagicMock()
        self.github_util._is_file_up_to_date.side_effect = [
            False,  # file is not up-to-date on main branch
            False  # file is not up-to-date on file-sync branch
        ]
        self.github_util._create_branch_if_not_exists = MagicMock()
        self.github_util._update_file = MagicMock()

        self.github_util.sync_files_for_repo(
            [FileConfig(source_path='foo/bar.yml', destination_path='foo/bar.yml', content=b'foo\n', sha='123')]
        )
        self.github_util._create_branch_if_not_exists.assert_called_once()
        self.github_util._create_branch_if_not_exists.assert_called_with('file-sync')
        self.github_util._update_file.assert_called_once()
        self.github_util._update_file.assert_called_with(
            FileConfig(source_path='foo/bar.yml', destination_path='foo/bar.yml', content=b'foo\n', sha='123'),
            branch='file-sync'
        )

    def test_delete_files_for_repo(self: Self) -> None:
        """Validate the delete_files_for_repo function is successful."""
        self.github_util.repository = MagicMock()
        self.github_util.repository.get_contents.return_value.sha = '123'
        self.github_util.repository.delete_file = MagicMock()

        self.github_util.delete_files_for_repo(
            [FileConfig(source_path='foo/bar.yml', destination_path='foo/bar.yml')]
        )
        self.github_util.repository.delete_file.assert_called_once()
        self.github_util.repository.delete_file.assert_called_with(
            path='foo/bar.yml', message='Deleted by file-sync', sha='123', branch='file-sync'
        )

    def test_delete_files_for_repo_with_exception(self: Self) -> None:
        """Validate the delete_files_for_repo function is successful."""
        self.github_util.repository = MagicMock()
        self.github_util.repository.get_contents.side_effect = UnknownObjectException(404)
        self.github_util.repository.delete_file = MagicMock()

        self.github_util.delete_files_for_repo(
            [FileConfig(source_path='foo/bar.yml', destination_path='foo/bar.yml')]
        )
        self.github_util.repository.delete_file.assert_not_called()
