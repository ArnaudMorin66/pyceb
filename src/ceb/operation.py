"""
Module contenant la classe CebOperation pour représenter une opération.
"""
from __future__ import annotations

from .base import CebBase


class CebOperation(CebBase):
    """
    Classe représentant une opération.

    Attributes:
        _value (int): La valeur résultante de l'opération.
        _operations (list): Liste des opérations effectuées.
    """

    def __init__(self, g: CebBase, op: str, d: CebBase):
        """ 
        Initialise une nouvelle instance de CebOperation.

        Args:
            g (CebBase): Le premier opérande.
            op (str): L'opération à effectuer.
            d (CebBase): Le second opérande.
        e.g.:
            CebOperation(CebPlaque(5), "+", CebPlaque(3))
        remark:
            Les opérandes sont inversés si le premier opérande est inférieur au second

            la valeur de l'opération est définie à 0 si le résultat est inutilisable
        """
        super().__init__()
        if g.value < d.value:
            g, d = d, g

        match op:
            # """
            # Effectue l'opération spécifiée sur les opérandes.
            # """
            case "+":
                self._value = g.value + d.value
            case "-":
                self._value = g.value - d.value
            case "x":
                self._value = g.value * d.value if g.value > 1 and d.value > 1 else 0
            case "/" | ":":
                self._value = (
                    g.value // d.value if d.value > 1 and g.value % d.value == 0 else 0
                )
            case _:
                self._value = 0
        if self._value != 0:
            """
            Met à jour la liste des opérations si la valeur résultante n'est pas nulle.
            """
            self._operations.clear()
            if isinstance(g, CebOperation):
                self._operations.extend(g.operations)
            if isinstance(d, CebOperation):
                self.operations.extend(d.operations)
            self._operations.append(f"{g._value} {op} {d._value} = {self._value}")
