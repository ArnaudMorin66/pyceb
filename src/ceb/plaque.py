"""
Importation
"""
from __future__ import annotations
from typing import List
from .base import CebBase
from .notify import IPlaqueNotify

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
    _observers: List[IPlaqueNotify] = []

    def __init__(self, v: int = 0, obs: IPlaqueNotify = None):
        super().__init__()
        self._value = v
        if obs:
            self._observers = [obs]
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
        self.notify_observers(old)

    def notify_observers(self, old: int):
        """
        Notifie les observateurs de la modification de la plaque.

        Args:
            old (int): L'ancienne valeur de la plaque.
        """
        for obs in self._observers:
            obs.plaque_notify(self, old)

    def add_observer(self, observer: IPlaqueNotify):
        """
        Ajoute un observateur à la liste.

        Args:
            observer (IPlaqueNotify): L'observateur à ajouter.
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: IPlaqueNotify):
        """
        Retire un observateur de la liste.

        Args:
            observer (IPlaqueNotify): L'observateur à retirer.
        """
        if observer in self._observers:
            self._observers.remove(observer)
