"""
Importation
"""
from __future__ import annotations

from typing import List, override

from utils import SignalBase


from .base import CebBase

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
STRPLAQUESUNIQUES = list(map(str, PLAQUESUNIQUES))


class CebPlaque(CebBase, SignalBase):
    """classe définissant une plaque du jeu"""

    def __init__(self, valeur_initiale: int = 0, observateur= None):
        super().__init__()
        SignalBase.__init__(self)
        self._value = valeur_initiale

        if observateur:
            self._observers.append(observateur)
        self.operations.append(str(valeur_initiale))

    @property
    def is_valid(self) -> int:
        """
        teste de la validité de la plaque
        """
        return self._value in PLAQUESUNIQUES

    @override
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
        self.emit(self, old)
