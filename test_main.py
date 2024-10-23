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
        os.environ['INPUT_PULL_REQUEST_BRANCH'] = 'file-sync'
        os.environ['INPUT_PULL_REQUEST_TITLE'] = 'my pull request'
        os.environ['INPUT_PULL_REQUEST_DRAFT'] = 'true'
        os.environ['INPUT_COMMIT_MESSAGE'] = 'updated files'
        os.environ['INPUT_TARGET_BRANCH'] = 'main2'

        main.GitHubUtil = MagicMock()
        main.GitHubUtil.get_repo_list_from_regex_patterns.return_value = ['destination_repo']

        sync_files = [FileConfig(source_path='./foo.txt', destination_path='./foo.txt', sha='123', content=b'test')]
        main.GitHubUtil().get_sync_files_from_source_repo.return_value = sync_files

        main.main()

        main.GitHubUtil().get_sync_files_from_source_repo.assert_called_once()
        main.GitHubUtil().get_sync_files_from_source_repo.assert_called_with('./foo.txt\n', 'main1')

        main.GitHubUtil().sync_files_for_repo.assert_called_once()
        main.GitHubUtil().sync_files_for_repo.assert_called_with(
            sync_files=sync_files, file_sync_branch='file-sync',
            base_branch='main2', commit_message='updated files'
        )

        main.GitHubUtil().delete_files_for_repo.assert_called_once()
        main.GitHubUtil().delete_files_for_repo.assert_called_with(
            delete_files=[FileConfig(source_path='./bar.txt', destination_path='./bar.txt')],
            message='updated files', file_sync_branch='file-sync', base_branch='main2'
        )

        main.GitHubUtil().create_pull_request.assert_called_once()
        main.GitHubUtil().create_pull_request.assert_called_with(head_branch='file-sync', base_branch='main2',
                                                                 title='my pull request', draft=True)

    def test_get_destination_repo_list(self: Self) -> None:
        """The destination repo list should be successfully loaded."""
        os.environ['INPUT_DESTINATION_REPOS'] = 'destination_repo1\ndestination_repo2\n'
        os.environ['INPUT_DESTINATION_REPOS_EXCLUDE'] = 'destination_repo3\n'

        main.GitHubUtil = MagicMock()
        main.GitHubUtil.get_repo_list_from_regex_patterns.return_value = [
            'destination_repo3',
            'destination_repo4',
            'destination_repo1',
        ]

        self.assertListEqual(
            ['destination_repo1', 'destination_repo2', 'destination_repo4', ], main._get_destination_repo_list()
        )
