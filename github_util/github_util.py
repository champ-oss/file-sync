"""Provides functionality for interfacing with GitHub repositories."""
import base64
import logging
from typing import Optional

from github import Github, Auth, UnknownObjectException, GithubException
from github.Repository import Repository
from typing_extensions import Self

from config_util.config_util import ConfigUtil
from config_util.file_config import FileConfig

logger = logging.getLogger(__name__)


class GitHubUtil:
    """Provides functionality for interfacing with GitHub repositories."""

    def __init__(self: Self, access_token: str, repository_name: str, github_session: Github = None) -> None:
        """
        Initialize the GitHub utility.

        :param access_token: GitHub personal access token
        :param github_session: authenticated session to GitHub
        """
        if not github_session:
            logger.debug('logging in to GitHub using access token')
            self.github_session = Github(auth=Auth.Token(access_token))
            self.repository: Repository = self._get_repo(self.github_session, repository_name)

        else:
            self.github_session = github_session

    @staticmethod
    def _get_repo(github_session: Github, repository_name: str) -> Optional[Repository]:
        """
        Get a repository by name in the format of 'owner/repo'.

        :param github_session: authenticated session to GitHub
        :param repository_name: name of the repository
        :return: GitHub repository
        """
        try:
            return github_session.get_repo(repository_name)
        except (UnknownObjectException, GithubException) as e:
            logger.warning(f'unable to find repository: {repository_name} error:{e}')
            return None

    def get_sync_files_from_source_repo(self: Self, action_input_files: str,
                                        branch: str = 'main') -> Optional[list[FileConfig]]:
        """
        Get the list of files to sync from the source repository.

        :param action_input_files: string of input files from the GitHub action
        :param branch: name of the branch to sync files from (default: main)
        :return: list of files to sync
        """
        if not self.repository:
            return None

        sync_files = ConfigUtil.parse_files_config_from_input(action_input_files)

        for sync_file in sync_files:
            template_file = self.repository.get_contents(sync_file.source_path, ref=branch)
            sync_file.sha = template_file.sha
            sync_file.content = base64.b64decode(template_file.content)
            logger.info(f'{self.repository.name}: loaded source file: {sync_file.source_path} sha:{sync_file.sha} '
                        f'bytes:{len(sync_file.content)}')

        return sync_files

    def sync_files_for_repo(self: Self, sync_files: list[FileConfig]) -> None:
        """
        Sync the list of files to the repository.

        :param sync_files: list of files to sync
        :return: None
        """
        if not self.repository:
            return

        logger.info(f'{self.repository.name}: starting sync process')
        for sync_file in sync_files:
            if self._is_file_up_to_date(sync_file, branch='main'):
                continue

            self._create_branch_if_not_exists('file-sync')

            if self._is_file_up_to_date(sync_file, branch='file-sync'):
                continue

            self._update_file(sync_file, branch='file-sync')

    def _create_branch_if_not_exists(self: Self, branch_name: str, source_branch: str = 'main') -> None:
        """
        Create a branch on the repository if it does not already exist.

        :param branch_name: name of the branch to create
        :param source_branch: source of the new branch (default: main)
        :return: None
        """
        try:
            branch = self.repository.get_branch(branch_name)
            if branch:
                return
        except (UnknownObjectException, GithubException) as e:
            logger.debug(e)

        logger.info(f'{self.repository.name}: creating {branch_name} branch')
        source_sha = self.repository.get_branch(source_branch).commit.sha
        self.repository.create_git_ref(ref=f'refs/heads/{branch_name}', sha=source_sha)

    def _is_file_up_to_date(self: Self, source_file: FileConfig, branch: str) -> bool:
        """
        Check if the source file is up-to-date in the destination repository by comparing the SHA.

        :param source_file: source file to check
        :param branch: which branch the file should be checked
        :return: true if the file is up-to-date, false if it needs to be updated
        """
        try:
            logger.info(f'{self.repository.name}: checking file: {source_file.destination_path}')
            destination_file = self.repository.get_contents(source_file.destination_path, ref=branch)
        except (UnknownObjectException, GithubException) as e:
            logger.debug(e)
            return False

        if destination_file.sha == source_file.sha:
            logger.info(f'{self.repository.name}: file is already up to date '
                        f'on {branch} branch: {source_file.destination_path}')
            return True

        logger.warning(f'{self.repository.name}: file needs to be updated '
                       f'on {branch} branch: {source_file.destination_path}')
        return False

    def _update_file(self: Self, sync_file: FileConfig, branch: str) -> None:
        """
        Update the file in the destination repository, or create a new file if it does not exist.

        :param sync_file: file to update
        :param branch: branch to push changes
        :return: None
        """
        try:
            destination_file = self.repository.get_contents(sync_file.destination_path, ref=branch)
            logger.info(f'{self.repository.name}: updating file: {sync_file.destination_path}')
            self.repository.update_file(path=sync_file.destination_path,
                                        message='Updated by file-sync',
                                        content=sync_file.content,
                                        sha=destination_file.sha,
                                        branch=branch)

        except (UnknownObjectException, GithubException) as e:
            logger.debug(e)
            logger.info(f'{self.repository.name}: creating file: {sync_file.destination_path}')
            self.repository.create_file(path=sync_file.destination_path,
                                        message='Updated by file-sync',
                                        content=sync_file.content,
                                        branch=branch)

    def create_pull_request(self: Self, head_branch: str, base_branch: str = 'main', draft: bool = False) -> None:
        """
        Create a pull request on the destination repository.

        :param head_branch: source branch for the pull request
        :param base_branch: target branch for the pull request (default: main)
        :param draft: create a draft pull request (default: False)
        :return:
        """
        if not self.repository:
            return

        try:
            pull_request = self.repository.create_pull(title='file-sync',
                                                       head=head_branch,
                                                       base=base_branch,
                                                       draft=draft)
            logger.info(f'{self.repository.name}: created pull request: {pull_request.html_url}')
        except GithubException as e:
            logger.debug(e)
