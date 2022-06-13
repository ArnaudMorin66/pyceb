"""
    Calcul du compte est bon
"""
from __future__ import annotations

import json
from random import randint
from typing import List
from sys import maxsize as MAXINT
from enum import Enum

"""
CebBase
"""


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


"""
CebPlaque
"""
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


"""
CebOperation
"""


class CebOperation(CebBase):

    def __init__(self, g: CebBase, op: str, d: CebBase):
        """
        definir une Opération
        @type g: CebBase
        @type op: str (+-x/)
        @type d: CebBase
        """
        super().__init__()
        if g._value < d._value:
            g, d = d, g

        match op:
            case "+":
                self._value = g._value + d._value
            case "-":
                self._value = g._value - d._value
            case "x":
                self._value = g._value * d._value if g._value > 1 and d._value > 1 else 0
            case "/":
                self._value = g._value // d._value \
                    if d._value > 1 and g._value % d._value == 0 else 0
            case _:
                self._value = 0
        if self._value != 0:
            self._operations.clear()
            if isinstance(g, CebOperation):
                self._operations.extend(g._operations)
            if isinstance(d, CebOperation):
                self.operations.extend(d.operations)
            self._operations.append(f"{g._value} {op} {d._value} = {self._value}")


"""
CebFind
"""


class CebStatus(Enum):
    """
    Status du compte
    """

    Indefini = 0
    Valide = 1
    EnCours = 2
    CompteEstBon = 3
    CompteApproche = 4
    Invalide = 5


class CebFind:
    def __init__(self):
        self._found1, self._found2 = MAXINT, -1

    @property
    def found1(self) -> int:
        return self._found1

    @property
    def found2(self) -> int:
        return self._found2

    def init(self, value: int = MAXINT) -> None:
        self._found1 = value
        self._found2 = -1

    def set(self, value: int) -> None:
        if value in (self._found1, self._found2):
            return
        elif self._found1 > value:
            self._found2, self._found1 = self._found1, value
        else:
            self._found2 = value

    @property
    def is_unique(self) -> bool:
        return self._found2 == -1

    def __repr__(self):
        return json.dumps({"found1": self._found1, "found2": self._found2})

    def __str__(self) -> str:
        return str(self._found1) + (f" et {self._found2}" if not self.is_unique else "")


class CebTirage:
    """
    Tirage Plaques et Recherche
    """
    _plaques: list[CebPlaque] = []
    _search: int = 0
    _solutions: List[CebBase] = []
    _diff: int = MAXINT
    _status: CebStatus = CebStatus.Indefini
    _found: CebFind = CebFind()

    def __init__(self, plaques: List[int] = (), search: int = 0) -> None:
        """

        @type search: int Valeur à chercher
        """
        for k in plaques:
            self._plaques.append(CebPlaque(k))
        self._search = search
        if search != 0 and len(plaques) > 0:
            self.valid()
        elif search == 0 and len(plaques) > 0:
            self._search = randint(100, 999)
            self.valid()
        else:
            self.random()

    def clear(self) -> CebStatus:
        self._solutions = []
        self._diff = MAXINT
        self._found.init()
        return self.valid()

    @property
    def found(self) -> CebFind:
        return self._found

    @property
    def search(self) -> int:
        return self._search

    @search.setter
    def search(self, value: int):
        self._search = value
        self.clear()

    def random(self) -> CebStatus:
        self.clear()
        self._search = randint(100, 999)
        liste_plaques = LISTEPLAQUES[:]
        self._plaques[:] = []
        while len(self._plaques) < 6:
            valeur_plaque = randint(0, len(liste_plaques) - 1)
            self._plaques.append(CebPlaque(liste_plaques[valeur_plaque]))
            del liste_plaques[valeur_plaque]
        # self.valid()
        self._status = CebStatus.Valide
        return self._status

    def _sol_to_json(self) -> str:
        return json.dumps(set([op.operations for op in self._solutions]))

    def to_json(self) -> str:
        return json.dumps(self.result)

    @property
    def diff(self) -> int:
        return self._diff

    @property
    def count(self) -> int:
        return len(self.solutions)

    @property
    def solutions(self) -> List[CebBase]:
        """

        :rtype: List[CebBase]
        """
        return self._solutions

    @property
    def status(self) -> CebStatus:
        return self._status

    @status.setter
    def status(self, value: CebStatus):
        self._status = value

    @property
    def plaques(self) -> List[CebPlaque]:
        return self._plaques

    @plaques.setter
    def plaques(self, value: List[CebPlaque | int]):
        self._plaques[:] = [k if not isinstance(k, int) else CebPlaque(k) for k in value]
        self.clear()

    def valid(self) -> CebStatus:
        """
        validation du tirae
        :return : CebStatus
        """
        if self._search not in range(100, 1000):
            self._status = CebStatus.Invalide
            return self._status
        if len(self.plaques) != 6:
            self._status = CebStatus.Invalide
            return self._status
        for plaque in self._plaques:
            count_plaques: int = LISTEPLAQUES.count(plaque.value)
            if count_plaques == 0 or count_plaques < self._plaques.count(plaque):
                self._status = CebStatus.Invalide
                return self._status
        self._status = CebStatus.Valide
        return self._status

    @property
    def solution(self) -> CebBase | None:
        return self.solutions[0] if self.count != 0 else None

    def _add_solution(self, sol: CebBase):
        """
            ajoute l'opération sol aux solutions si valeur est plus proche ou égale
            à celles déjà trouvées
        @param sol:
        @return: rien
        """
        diff: int = abs(sol.value - self._search)
        if diff > self._diff:
            return
        if diff != self._diff:
            self._solutions = [sol]
            self._found.init(sol.value)
            self._diff = diff
        elif sol not in self._solutions:
            self._solutions.append(sol)
            self._found.set(sol.value)

    def resolve(self, plaques: List[CebPlaque | int] = (), search: int = 0) -> CebStatus:
        """

        :rtype: object
        """
        if search != 0 and len(plaques) == 6:
            self._search = search
            self.plaques = plaques
        self.clear()
        if self._status == CebStatus.Invalide:
            return self._status
        self._status = CebStatus.EnCours
        self._resolve(self.plaques[:])
        self._solutions.sort(key=lambda sol: sol.rank)
        self.status = CebStatus.CompteEstBon \
            if self.solutions[0].value == self._search else CebStatus.CompteApproche
        return self._status

    def _resolve(self, lplaques: List) -> None:
        for i, p in enumerate(lplaques):
            self._add_solution(p)
            for j in range(i + 1, len(lplaques)):
                q = lplaques[j]
                for operation in "+x/-":
                    oper = CebOperation(p, operation, q)
                    if oper.value != 0:
                        self._resolve([oper] +
                                      [x for k, x in enumerate(lplaques) if k not in (i, j)])

    @property
    def result(self) -> dict:
        return {
            "Search": self.search,
            "Plaques": [p.value for p in self._plaques],
            "Status": self._status.name,
            "Found": str(self.found),
            "Diff": self.diff,
            "Solutions": [str(s) for s in self.solutions]}

    @property
    def data(self) -> tuple:
        return self.search, self.plaques

    def __repr__(self):
        return self.to_json()

    @staticmethod
    def solve(plaques: List[int] = (), search: int = 0) -> CebTirage:
        _tirage = CebTirage(plaques, search)
        _tirage.resolve()
        return _tirage


if __name__ == "__main__":
    print(CebTirage.solve())
