import datetime
from dataclasses import dataclass

# This class represents a simple database that stores its data as files in a directory.
class DB:
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
    improve: DB


def archive(dbs: DBs):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dbs.archive.data[dbs.archive.identifier][timestamp] = {
        "memory": dbs.memory.data[dbs.memory.identifier],
        "workspace": dbs.workspace.data[dbs.workspace.identifier]
    }
    return []
