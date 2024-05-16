"""Provides functionality for loading configuration options."""
import logging
import os

from config_util.file_config import FileConfig

logger = logging.getLogger(__name__)


class ConfigUtil:
    """Provides functionality for loading configuration options."""

    @staticmethod
    def parse_files_config_from_input(action_input_files: str) -> list[FileConfig]:
        """
        Parse the GitHub action input string into a list of FileConfig objects.

        :param action_input_files: files input from the GitHub action
        :return: list of FileConfig objects
        """
        logger.debug(f'parsing input: {action_input_files}')
        files_config: list[FileConfig] = []

        for line in action_input_files.split('\n'):
            if line.strip() == '':
                continue

            if '=' in line:
                source, destination = line.split('=')
                files_config.append(FileConfig(source.strip(), destination.strip()))
                logger.debug(f'configured file: {source.strip()}')
            else:
                files_config.append(FileConfig(line.strip(), line.strip()))
                logger.debug(f'configured file: {line.strip()}')

        return files_config

    @staticmethod
    def parse_list_from_input(action_input: str) -> list[str]:
        """
        Parse the GitHub action input string into a list of strings.

        :param action_input: input from the GitHub action
        :return: list of strings
        """
        results = []
        if not action_input:
            return results
        for line in action_input.split('\n'):
            if line.strip() == '':
                continue
            results.append(line.strip())
        return results

    @staticmethod
    def token() -> str:
        """Load the config value from the environment variables."""
        return os.getenv('INPUT_TOKEN')

    @staticmethod
    def source_repo_name() -> str:
        """Load the config value from the environment variables."""
        return os.getenv('INPUT_SOURCE_REPO')

    @staticmethod
    def source_repo_branch() -> str:
        """Load the config value from the environment variables."""
        return os.getenv('INPUT_SOURCE_REPO_BRANCH')

    @staticmethod
    def files() -> str:
        """Load the config value from the environment variables."""
        return os.getenv('INPUT_FILES')

    @staticmethod
    def delete_files() -> str:
        """Load the config value from the environment variables."""
        return os.getenv('INPUT_DELETE_FILES')

    @staticmethod
    def destination_repos() -> str:
        """Load the config value from the environment variables."""
        if not os.getenv('INPUT_DESTINATION_REPOS') and not os.getenv('INPUT_DESTINATION_REPOS_REGEX'):
            return os.getenv('INPUT_CURRENT_REPOSITORY')

        return os.getenv('INPUT_DESTINATION_REPOS')

    @staticmethod
    def destination_repos_regex() -> str:
        """Load the config value from the environment variables."""
        return os.getenv('INPUT_DESTINATION_REPOS_REGEX')

    @staticmethod
    def pull_request_draft() -> bool:
        """Load the config value from the environment variables."""
        return os.getenv('INPUT_PULL_REQUEST_DRAFT', 'false').lower() == 'true'

    @staticmethod
    def pull_request_branch() -> str:
        """Load the config value from the environment variables."""
        return os.getenv('INPUT_PULL_REQUEST_BRANCH')
