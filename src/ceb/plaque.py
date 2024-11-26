"""
Importation
"""
from __future__ import annotations
from typing import List
from .base import CebBase
from .inotify import INotify

#: Liste des plaques disponibles
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

#: Liste des plaques uniques, triées
PLAQUESUNIQUES = sorted(set(LISTEPLAQUES))

#: Liste des plaques uniques sous forme de chaînes de caractères
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


    def set_value(self, valeur: int):
        """
        Met à jour la valeur de la plaque.

        Args:
            valeur (int): La nouvelle valeur de la plaque.

        Raises:
            ValueError: Si la nouvelle valeur est invalide.
        """
        if valeur == self.value:
            return
        old = self.value
        super().set_value(valeur)
        self.operations[0] = str(valeur)
        if self._observer:
            self._observer.notify(self, old)
