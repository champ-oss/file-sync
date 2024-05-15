"""Represents the configuration for a file to sync."""
from dataclasses import dataclass


@dataclass
class FileConfig:
    """Represents the configuration for a file to sync."""

    source_path: str
    destination_path: str
    sha: str = None
    content: bytes = None
