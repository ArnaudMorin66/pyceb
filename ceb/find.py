# from __future__ import annotations

import json
import sys


class CebFind:
    def __init__(self):
        self._found1, self._found2 = sys.maxsize, -1

    @property
    def found1(self) -> int:
        return self._found1

    @property
    def found2(self) -> int:
        return self._found2

    def reset(self, value: int = sys.maxsize) -> None:
        self._found1 = value
        self._found2 = -1

    def set(self, value: int) -> None:
        if value in (self._found1, self._found2):
            return
        if self._found1 > value:
            self._found2, self._found1 = self._found1, value
        else:
            self._found2 = value

    @property
    def is_unique(self) -> bool:
        return self._found2 == -1

    def __repr__(self):
        return json.dumps({"found1": self._found1, "found2": self._found2})

    def __str__(self) -> str:
        return str(self._found1) + (f" et {self._found2}" if not self.is_unique else "")
