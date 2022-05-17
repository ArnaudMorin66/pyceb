from __future__ import annotations

from typing import List


class CebBase:
    """
    Classe de base
    """

    def __init__(self) -> None:
        self._value: int = 0
        self._operations: List[str] = []

    @property
    def value(self) -> int:
        """

        :rtype: int
        """
        return self._value

    @value.setter
    def value(self, valeur: int):
        """
        """
        self._value = valeur

    @property
    def rank(self) -> int:
        """
        Retourne le rang
        :return : int
        """
        return len(self._operations)

    @property
    def operations(self) -> List[str]:
        """
        :return : Liste des opérations
        """
        return self._operations

    def __repr__(self) -> str:
        return ", ".join(self._operations)

    def __eq__(self, other: CebBase) -> bool:
        return self._operations == other.operations
