"""Provides tests for GitHub utility."""
import unittest
from unittest.mock import MagicMock

from github import UnknownObjectException, GithubException
from typing_extensions import Self

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
