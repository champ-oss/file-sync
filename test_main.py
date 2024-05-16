"""Provide tests for main script."""
import os
import unittest
from unittest.mock import MagicMock

from typing_extensions import Self

import main
from config_util.file_config import FileConfig


class TestMain(unittest.TestCase):
    """Provide tests for main script."""

    def test_main(self: Self) -> None:
        """The main function should be successful."""
        os.environ['INPUT_FILES'] = './foo.txt\n'
        os.environ['INPUT_DELETE_FILES'] = './bar.txt\n'
        os.environ['INPUT_DESTINATION_REPOS'] = 'destination_repo\n'
        os.environ['INPUT_SOURCE_REPO_BRANCH'] = 'main1'
        os.environ['INPUT_PULL_REQUEST_BRANCH'] = 'main2'
        os.environ['INPUT_PULL_REQUEST_DRAFT'] = 'true'

        main.GitHubUtil = MagicMock()

        sync_files = [FileConfig(source_path='./foo.txt', destination_path='./foo.txt', sha='123', content=b'test')]
        main.GitHubUtil().get_sync_files_from_source_repo.return_value = sync_files

        main.main()

        main.GitHubUtil().get_sync_files_from_source_repo.assert_called_once()
        main.GitHubUtil().get_sync_files_from_source_repo.assert_called_with(
            action_input_files='./foo.txt\n', branch='main1'
        )

        main.GitHubUtil().sync_files_for_repo.assert_called_once()
        main.GitHubUtil().sync_files_for_repo.assert_called_with(sync_files)

        main.GitHubUtil().delete_files_for_repo.assert_called_once()
        main.GitHubUtil().delete_files_for_repo.assert_called_with(
            [FileConfig(source_path='./bar.txt', destination_path='./bar.txt')]
        )

        main.GitHubUtil().create_pull_request.assert_called_once()
        main.GitHubUtil().create_pull_request.assert_called_with(head_branch='main2', draft=True)
