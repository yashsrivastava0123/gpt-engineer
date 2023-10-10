"""
Module for simple file-based key-value database management.

This module provides a simple file-based key-value database system, where keys are
represented as filenames and values are the contents of these files. The primary class,
DB, is responsible for the CRUD operations on the database. Additionally, the module
provides a dataclass `DBs` that encapsulates multiple `DB` instances to represent different
databases like memory, logs, preprompts, etc.

Functions:
    archive(dbs: DBs) -> None:
        Archives the memory and workspace databases, moving their contents to
        the archive database with a timestamp.

Classes:
    DB:
        A simple key-value store implemented as a file-based system.

    DBs:
        A dataclass containing multiple DB instances representing different databases.

Imports:
    - datetime: For timestamp generation when archiving.
    - shutil: For moving directories during archiving.
    - dataclasses: For the DBs dataclass definition.
    - pathlib: For path manipulations.
    - typing: For type annotations.
"""

import datetime
from dataclasses import dataclass

# This class represents a simple database that stores its data as files in a directory.
class DB:
    """
    A file-based key-value store where keys correspond to filenames and values to file contents.

    This class provides an interface to a file-based database, leveraging file operations to
    facilitate CRUD-like interactions. It allows for quick checks on the existence of keys,
    retrieval of values based on keys, and setting new key-value pairs.

    Attributes
    ----------
    path : Path
        The directory path where the database files are stored.

    Methods
    -------
    __contains__(key: str) -> bool:
        Check if a file (key) exists in the database.

    __getitem__(key: str) -> str:
        Retrieve the content of a file (value) based on its name (key).

    get(key: str, default: Optional[Any] = None) -> Any:
        Fetch content of a file or return a default value if it doesn't exist.

    __setitem__(key: Union[str, Path], val: str):
        Set or update the content of a file in the database.

    Note:
    -----
    Care should be taken when choosing keys (filenames) to avoid potential
    security issues, such as directory traversal. The class implements some checks
    for this but it's essential to validate inputs from untrusted sources.
    """

    """A simple key-value store, where keys are filenames and values are file contents."""

    def __init__(self, data: dict, identifier: str):
        self.data = data
        self.identifier = identifier
        if self.identifier not in self.data:
            self.data[self.identifier] = {}

    def __contains__(self, key):
        return key in self.data[self.identifier]

    def __getitem__(self, key):
        if key not in self.data[self.identifier]:
            raise KeyError(f"Key '{key}' not found")
        return self.data[self.identifier][key]

    def get(self, key, default=None):
        return self.data[self.identifier].get(key, default)

    def __setitem__(self, key, val):
        self.data[self.identifier][key] = val


# dataclass for all dbs:
@dataclass
class DBs:
    memory: DB
    logs: DB
    preprompts: DB
    input: DB
    workspace: DB
    archive: DB
    project_metadata: DB


def archive(dbs: DBs):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dbs.archive.data[dbs.archive.identifier][timestamp] = {
        "memory": dbs.memory.data[dbs.memory.identifier],
        "workspace": dbs.workspace.data[dbs.workspace.identifier]
    }
    return []
