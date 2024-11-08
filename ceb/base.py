""" classe de base CebBase (Plaque ou Opération) """
from __future__ import annotations

from typing import List


class CebBase:
    """
    Classe de base 
    """

    _value: int
    _operations: List[str]

    def __init__(self) -> None:
        self._value = 0
        self._operations = []

    @property
    def value(self) -> int:
        """

        :rtype: int
        """
        return self._value

    def _set_value(self, valeur: int):
        self._value = valeur

    @value.setter
    def value(self, valeur: int):
        """ """
        self._set_value(valeur)

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

    @property
    def op1(self)-> str:
        return self._operations[0] if len(self._operations) > 0 else ""

    @property
    def op2(self)-> str:
        return self._operations[1] if len(self._operations) > 1 else ""

    @property
    def op3(self)-> str:
        return self._operations[2] if len(self._operations) > 2 else ""

    @property
    def op4(self)-> str:
        return self._operations[3] if len(self._operations) > 3 else ""

    @property
    def op5(self)-> str:
        return self._operations[4] if len(self._operations) >4 else ""
