"""Provides functionality for interfacing with GitHub repositories."""
import logging
from typing import Optional

from github import Github, Auth, UnknownObjectException, GithubException
from github.Repository import Repository
from typing_extensions import Self

logger = logging.getLogger(__name__)


class GitHubUtil:
    """Provides functionality for interfacing with GitHub repositories."""

    def __init__(self: Self, access_token: str, github_session: Github = None) -> None:
        """
        Initialize the GitHub utility.

        :param access_token: GitHub personal access token
        :param github_session: authenticated session to GitHub
        """
        if not github_session:
            logger.info('logging in to GitHub using access token')
            self.github_session = Github(auth=Auth.Token(access_token))
        else:
            self.github_session = github_session

    def get_repo(self: Self, repo_name: str) -> Optional[Repository]:
        """
        Get a repository by name in the format of 'owner/repo'.

        :param repo_name: name of the repository
        :return: GitHub repository
        """
        try:
            return self.github_session.get_repo(repo_name)
        except (UnknownObjectException, GithubException) as e:
            logger.warning(f'unable to find repository: {repo_name} error:{e}')
            return None

    @staticmethod
    def create_branch_if_not_exists(repo: Repository, branch_name: str, source_branch: str = 'main') -> None:
        """
        Create a branch on the repository if it does not already exist.

        :param repo: repository to create branch
        :param branch_name: name of the branch to create
        :param source_branch: source of the new branch (default: main)
        :return: None
        """
        try:
            branch = repo.get_branch(branch_name)
            if branch:
                return
        except GithubException as e:
            logger.debug(e)

        logger.info(f'{repo.name}: creating {branch_name} branch')
        source_sha = repo.get_branch(source_branch).commit.sha
        repo.create_git_ref(ref=f'refs/heads/{branch_name}', sha=source_sha)
