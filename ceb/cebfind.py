from __future__ import annotations

import json

MAXINT: int = 99999999


class CebFind:
    def __init__(self):
        self._found1, self._found2 = 0, -1
        self.init()

    @property
    def found1(self) -> int:
        return self._found1

    @property
    def found2(self) -> int:
        return self._found2

    def init(self, value: int = MAXINT) -> None:
        self._found1 = value
        self._found2 = -1

    def set(self, value: int) -> None:
        if value in (self._found1, self._found2):
            return
        elif self._found1 > value:
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
