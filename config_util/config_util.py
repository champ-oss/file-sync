"""Provides functionality for loading configuration options."""
import logging

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
                logger.info(f'configured source file: {source.strip()}')
            else:
                files_config.append(FileConfig(line.strip(), line.strip()))
                logger.info(f'configured source file: {line.strip()}')

        return files_config

    @staticmethod
    def parse_list_from_input(action_input: str) -> list[str]:
        """
        Parse the GitHub action input string into a list of strings.

        :param action_input: input from the GitHub action
        :return: list of strings
        """
        results = []
        for line in action_input.split('\n'):
            if line.strip() == '':
                continue
            results.append(line.strip())
        return results
