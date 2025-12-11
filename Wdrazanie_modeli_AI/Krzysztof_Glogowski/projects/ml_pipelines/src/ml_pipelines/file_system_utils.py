from copy import deepcopy

import fsspec
from fsspec import AbstractFileSystem
from kedro.io.core import get_protocol_and_path


def get_filesystem(
    path: str, fs_args: dict | None = None, credentials: dict | None = None
) -> AbstractFileSystem:
    _fs_args = deepcopy(fs_args) or {}
    _credentials = deepcopy(credentials) or {}

    protocol, _ = get_protocol_and_path(path)
    if protocol == "file":
        _fs_args.setdefault("auto_mkdir", True)

    return fsspec.filesystem(protocol, **{**_credentials, **_fs_args})
