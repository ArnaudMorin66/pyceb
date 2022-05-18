from __future__ import annotations

from typing import List

from .cebbase import CebBase

LISTEPLAQUES: List[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 25, 50, 75, 100,
                           1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 25]
PLAQUESUNIQUES: list[int] = list(set(LISTEPLAQUES))


class CebPlaque(CebBase):
    def __init__(self, v=0):
        super().__init__()
        self._value = v
        self.operations.extend([str(v)])
