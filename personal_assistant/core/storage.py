"""Persistence layer.

Storage — minimal save/load interface.
PickleStorage — pickle-backed with atomic write (tempfile + os.replace).
Atomicity protects the file if the process dies mid-write.
"""

from __future__ import annotations

import os
import pickle
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, TypeVar

T = TypeVar("T")


class Storage(ABC):
    @abstractmethod
    def save(self, obj: object, path: Path) -> None: ...

    @abstractmethod
    def load(self, path: Path, default_factory: Callable[[], T]) -> T: ...


class PickleStorage(Storage):
    def save(self, obj: object, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(
            prefix=path.name + ".",
            suffix=".tmp",
            dir=str(path.parent),
        )
        try:
            with os.fdopen(fd, "wb") as f:
                pickle.dump(obj, f)
            os.replace(tmp_name, path)
        except Exception:
            try:
                os.unlink(tmp_name)
            except FileNotFoundError:
                pass
            raise

    def load(self, path: Path, default_factory: Callable[[], T]) -> T:
        path = Path(path)
        if not path.exists():
            return default_factory()
        with open(path, "rb") as f:
            return pickle.load(f)