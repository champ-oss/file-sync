"""Provides tests for Config utility."""
import os
import unittest

from typing_extensions import Self

from config_util.config_util import ConfigUtil
from config_util.file_config import FileConfig


class TestConfigUtil(unittest.TestCase):
    """Provides tests for Config utility."""

    def test_parse_files_config_from_input(self: Self) -> None:
        """The parse_files function should be successful."""
        expected = [
            FileConfig(source_path='file1', destination_path='file1'),
            FileConfig(source_path='file2', destination_path='file2'),
            FileConfig(source_path='file3', destination_path='file3'),
        ]
        self.assertEqual(expected, ConfigUtil.parse_files_config_from_input('file1\nfile2\nfile3\n'))

        expected = [
            FileConfig(source_path='file1', destination_path='file1'),
            FileConfig(source_path='file2a', destination_path='file2b'),
        ]
        self.assertEqual(expected, ConfigUtil.parse_files_config_from_input('file1\nfile2a=file2b\n'))

        expected = [
            FileConfig(source_path='file1', destination_path='file1'),
            FileConfig(source_path='file2a', destination_path='file2b'),
        ]
        self.assertEqual(expected, ConfigUtil.parse_files_config_from_input('file1\n file2a=file2b\n '))

        expected = [
            FileConfig(source_path='file1a', destination_path='/tmp/foo/file1b'),
            FileConfig(source_path='/tmp/bar1/file2a', destination_path='/tmp/bar2/file2b'),
        ]
        self.assertEqual(expected, ConfigUtil.parse_files_config_from_input(
            'file1a=/tmp/foo/file1b\n/tmp/bar1/file2a=/tmp/bar2/file2b\n'
        ))

    def test_parse_list_from_input(self: Self) -> None:
        """The parse_list_from_input function should be successful."""
        self.assertEqual(['item1'], ConfigUtil.parse_list_from_input('item1'))
        self.assertEqual(['item1'], ConfigUtil.parse_list_from_input(' item1\n '))
        self.assertEqual(['item1', 'item2', 'item3'], ConfigUtil.parse_list_from_input('item1\nitem2\nitem3\n'))
        self.assertEqual(['item1', 'item2', 'item3'], ConfigUtil.parse_list_from_input('item1\n item2 \nitem3\n'))
        self.assertEqual(['item1', 'item2', 'item3'], ConfigUtil.parse_list_from_input(' item1\n item2 \nitem3\n '))
        self.assertEqual([], ConfigUtil.parse_list_from_input(''))
        self.assertEqual([], ConfigUtil.parse_list_from_input(None))

    def test_load_configs(self: Self) -> None:
        """The functions to load variables should be successful."""
        os.environ['INPUT_TOKEN'] = 'test_token'
        self.assertEqual('test_token', ConfigUtil.token())

        os.environ['INPUT_SOURCE_REPO'] = 'test_source_repo_name'
        self.assertEqual('test_source_repo_name', ConfigUtil.source_repo_name())

        os.environ['INPUT_SOURCE_REPO_BRANCH'] = 'main'
        self.assertEqual('main', ConfigUtil.source_repo_branch())

        os.environ['INPUT_FILES'] = 'foo\bbar'
        self.assertEqual('foo\bbar', ConfigUtil.files())

        os.environ['INPUT_DELETE_FILES'] = 'foo123\bbar123'
        self.assertEqual('foo123\bbar123', ConfigUtil.delete_files())

        os.environ['INPUT_DESTINATION_REPOS'] = 'test1\btest2'
        self.assertEqual('test1\btest2', ConfigUtil.destination_repos())

        os.environ['INPUT_DESTINATION_REPOS_REGEX'] = 'test3\btest4'
        self.assertEqual('test3\btest4', ConfigUtil.destination_repos_regex())

        os.environ['INPUT_DESTINATION_REPOS_EXCLUDE'] = 'test5\btest6'
        self.assertEqual('test5\btest6', ConfigUtil.destination_repos_exclude())

        os.environ['INPUT_PULL_REQUEST_DRAFT'] = 'true'
        self.assertEqual(True, ConfigUtil.pull_request_draft())

        os.environ['INPUT_PULL_REQUEST_BRANCH'] = 'test'
        self.assertEqual('test', ConfigUtil.pull_request_branch())

        # If both destination repo inputs are empty then the current repo should be used.
        os.environ['INPUT_DESTINATION_REPOS'] = ''
        os.environ['INPUT_DESTINATION_REPOS_REGEX'] = ''
        os.environ['INPUT_CURRENT_REPOSITORY'] = 'foo1'
        self.assertEqual('foo1', ConfigUtil.destination_repos())
