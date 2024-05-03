"""Provide tests for main script."""
import unittest

from typing_extensions import Self

import main


class TestMain(unittest.TestCase):
    """Provide tests for main script."""

    def test_main(self: Self) -> None:
        """The main function should be successful."""
        with self.assertLogs(level='WARNING') as logs:
            main.main()
            self.assertIn('not implemented', logs.output[0])
