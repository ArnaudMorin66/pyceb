"""
Importation
"""
from __future__ import annotations

from typing import List

from .base import CebBase
from .inotify import INotify

LISTEPLAQUES: List[int] = [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    25,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    25,
    50,
    75,
    100
]

PLAQUESUNIQUES = sorted(set(LISTEPLAQUES))
STRPLAQUESUNIQUES = [str(x) for x in PLAQUESUNIQUES]

class CebPlaque(CebBase):
    """
        classe définissant une plaque du jeu 
    """
    _observer: INotify = None

    def __init__(self, v: int = 0, obs: INotify = None):
        super().__init__()
        self._observer = obs
        self._value = v
        if not self.is_valid:
            raise ValueError(f"Valeur {v} invalide")
        self.operations.append(str(v))

    @property
    def is_valid(self) -> int:
        """
        teste de la validité de la plaque
        """
        return self._value in PLAQUESUNIQUES

    def _set_value(self, valeur: int):
        if valeur == self.value:
            return
        old = self.value
        super()._set_value(valeur)
        self.operations[0] = str(valeur)
        if self._observer:
            self._observer.notify(self, old)
