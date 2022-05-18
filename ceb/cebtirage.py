"""
    Calcul du compte est bon
"""
from __future__ import annotations

import json
from random import randint
from typing import List

from .cebfind import CebFind, MAXINT
from .cebplaque import CebPlaque, LISTEPLAQUES
from .ceboperation import CebOperation
from .cebstatus import CebStatus
from .cebbase import CebBase


class CebTirage:
    """
    Tirage Plaques et Recherche
    """

    def __init__(self, plaques: List[int] = (), search: int = 0) -> None:
        self._plaques: List[CebPlaque] = []
        for _, k in enumerate(plaques):
            self._plaques.append(CebPlaque(k))
        self._search: int = search
        self._found: CebFind = CebFind()
        self._solutions: List[CebBase] = []
        self._diff: int = MAXINT
        self._status: CebStatus = CebStatus.Indefini
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
        for _ in range(6):
            valeur_plaque = randint(0, len(liste_plaques) - 1)
            self._plaques.append(CebPlaque(liste_plaques[valeur_plaque]))
            del liste_plaques[valeur_plaque]
        self.valid()
        return self.status

    def _sol_to_json(self) -> str:
        return json.dumps([op.operations for op in self._solutions])

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
    def plaques(self, value: List[CebPlaque] | List[int]):
        self._plaques[:] = []
        for element in value:
            if isinstance(element, int):
                self._plaques.append(CebPlaque(element))
            elif isinstance(element, CebPlaque):
                self._plaques.append(element)
            else:
                raise ValueError("Errur instance value")
        self.clear()

    def valid(self) -> CebStatus:
        """
        validation du tirae
        :return : CebStatus
        """
        if self._search not in range(100, 1000):
            self.status = CebStatus.Invalide
            return self.status
        if len(self.plaques) != 6:
            self.status = CebStatus.Invalide
            return self.status
        for plaque in self._plaques:
            count_plaques = LISTEPLAQUES.count(plaque.value)
            if count_plaques == 0 or count_plaques < self._plaques.count(plaque):
                self.status = CebStatus.Invalide
                return self.status
        self.status = CebStatus.Valide
        return self.status

    @property
    def solution(self) -> CebBase | None:
        return self.solutions[0] if self.count != 0 else None

    def _push_solution(self, sol: CebBase):
        diff = abs(sol.value - self._search)
        if diff > self._diff:
            return
        if diff != self._diff:
            self._solutions = [sol]
            self._found.init(sol.value)
            self._diff = diff
        elif sol not in self._solutions:
            self._solutions.append(sol)
            self._found.set(sol.value)

    def resolve(self, plaques: List[int] = (), search: int = 0) -> CebStatus:
        """

        :rtype: object
        """
        if search != 0 and len(plaques) == 6:
            self._search = search
            self.plaques = plaques
        self.clear()
        if self.status == CebStatus.Invalide:
            return self.status
        self._status = CebStatus.EnCours
        self._resolve(self.plaques[:])
        self._solutions.sort(key=lambda sol: sol.rank)
        self.status = CebStatus.CompteEstBon \
            if self.solutions[0].value == self._search else CebStatus.CompteApproche
        return self.status

    def _resolve(self, lplaques: List) -> None:
        for i, p in enumerate(lplaques):
            self._push_solution(p)
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
            "Status": self.status.name,
            "Found": str(self.found),
            "Diff": self.diff,
            "Solutions": [str(s) for s in self.solutions]}

    @property
    def data(self) -> tuple:
        return self.search, self.plaques

    def __repr__(self):
        return self.to_json()

    @staticmethod
    def solve(plaques: List[int] = (), search: int = 0) -> dict:
        _tirage = CebTirage(plaques, search)
        _tirage.resolve()
        return _tirage.result


if __name__ == "__main__":
    print(CebTirage.solve())
