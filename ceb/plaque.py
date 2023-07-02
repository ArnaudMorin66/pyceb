from __future__ import annotations
from typing import List
from ceb.base import CebBase
from ceb.observer import Observer

LISTEPLAQUES: List[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 25, 50, 75, 100,
                           1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 25]
PLAQUESUNIQUES: list[int] = list(set(LISTEPLAQUES))


class CebPlaque(CebBase):
    _observer: Observer = None

    def __init__(self, v: int = 0, observer: Observer = None):
        super().__init__()
        self._value = v
        if not self.is_valid:
            raise ValueError(f"Valeur {v} invalide")
        self.operations.extend([str(v)])
        if observer is not None:
            self._observer = observer

    @property
    def is_valid(self) -> int:
        return self._value in PLAQUESUNIQUES

    def _set_value(self, valeur: int):
        super()._set_value(valeur)
        self.operations[0] = str(valeur)
        if self._observer is not None:
            self._observer.notify()
