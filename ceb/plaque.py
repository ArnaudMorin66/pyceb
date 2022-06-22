from __future__ import annotations
from ceb.base import CebBase

LISTEPLAQUES: List[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 25, 50, 75, 100,
                           1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 25]
PLAQUESUNIQUES: list[int] = list(set(LISTEPLAQUES))


class CebPlaque(CebBase):
    def __init__(self, v: int = 0):
        super().__init__()
        self._value = v
        if not self.is_valid:
            raise ValueError(f"Valeur {v} invalide")
        self.operations.extend([str(v)])

    @property
    def is_valid(self) -> int:
        return self._value in PLAQUESUNIQUES
