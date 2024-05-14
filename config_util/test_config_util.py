"""Provides tests for Config utility."""
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
