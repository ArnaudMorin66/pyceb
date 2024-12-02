""" classe de base CebBase (Plaque ou Opération) """
from __future__ import annotations

from typing import List

from utils import ObservableBase


class CebBase:
    """
    Classe de base pour les objets CebBase, représentant une plaque ou une opération.
    """

    _value: int
    _operations: List[str]

    def __init__(self) -> None:
        """
        Initialise une nouvelle instance de CebBase avec une valeur par défaut de 0
        et une liste vide d'opérations.
        """
        super().__init__()
        self._value = 0
        self._operations = []

    @property
    def value(self) -> int:
        """
        Retourne la valeur actuelle de l'objet.

        :rtype: int
        """
        return self._value

    @value.setter
    def value(self, valeur: int):
        """
        Définit la valeur de l'objet via le setter de la propriété.

        :param valeur: La nouvelle valeur à définir.
        """
        self.set_value(valeur)

    def set_value(self, valeur: int):
        """
        Définit la valeur de l'objet.

        :param valeur: La nouvelle valeur à définir.
        """
        self._value = valeur

    @property
    def rank(self) -> int:
        """
        Retourne le rang de l'objet, basé sur le nombre d'opérations.

        :return : int
        """
        return len(self._operations)

    @property
    def operations(self) -> List[str]:
        """
        Retourne la liste des opérations de l'objet.

        :return : Liste des opérations
        """
        return self._operations

    def __repr__(self) -> str:
        """
        Retourne une représentation en chaîne de caractères de l'objet,
        composée des opérations séparées par des virgules.

        :return: str
        """
        return ", ".join(self._operations)

    def __eq__(self, other: CebBase) -> bool:
        """
        Compare l'objet actuel avec un autre objet CebBase pour l'égalité.

        :param other: L'autre objet CebBase à comparer.
        :return: bool
        """
        return self._operations == other.operations

    @property
    def op1(self) -> str:
        """
        Retourne la première opération si elle existe, sinon une chaîne vide.

        :return: str
        """
        return self._operations[0] if len(self._operations) > 0 else ""

    @property
    def op2(self) -> str:
        """
        Retourne la deuxième opération si elle existe, sinon une chaîne vide.

        :return: str
        """
        return self._operations[1] if len(self._operations) > 1 else ""

    @property
    def op3(self) -> str:
        """
        Retourne la troisième opération si elle existe, sinon une chaîne vide.

        :return: str
        """
        return self._operations[2] if len(self._operations) > 2 else ""

    @property
    def op4(self) -> str:
        """
        Retourne la quatrième opération si elle existe, sinon une chaîne vide.

        :return: str
        """
        return self._operations[3] if len(self._operations) > 3 else ""

    @property
    def op5(self) -> str:
        """
        Retourne la cinquième opération si elle existe, sinon une chaîne vide.

        :return: str
        """
        return self._operations[4] if len(self._operations) > 4 else ""
