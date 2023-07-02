"""
    Calcul du compte est bon
"""
from __future__ import annotations

import asyncio
import json
from random import randint
from sys import maxsize
from typing import List

from builtins import list

from ceb.base import CebBase
from ceb.observer import Observer
from ceb.operation import CebOperation
from ceb.plaque import CebPlaque, LISTEPLAQUES
from ceb.status import CebStatus


class CebTirage:
    """
    Tirage Plaques et Recherche
    """

    def update(self, observer):
        self.clear()

    _observer: Observer

    def __init__(self, plaques: List[int] = (), search: int = 0, auto: bool = False) -> None:
        """

        @type search: int Valeur à chercher
        """
        self.auto: bool = auto
        self._plaques: List[CebPlaque] = []
        self._search: int = 0
        self._solutions: List[CebBase] = []
        self._diff: int = maxsize
        self._status: CebStatus = CebStatus.Indefini
        self._observer = Observer()
        self._observer.attach(self)
        for k in plaques:
            self._plaques.append(CebPlaque(k, self._observer))

        self._search = search
        if search != 0 and len(plaques) > 0:
            self.clear()
        elif search == 0 and len(plaques) > 0:
            self._search = randint(100, 999)
            self.clear()
        else:
            self.random()

    def clear(self) -> CebStatus:
        self._solutions = []
        self._diff = maxsize
        self.valid()
        if self.auto:
            self.resolve()
        return self.status

    @property
    def found(self) -> list[int]:
        return sorted(set([k.value for k in self.solutions]))

    @property
    def search(self) -> int:
        return self._search

    @search.setter
    def search(self, value: int):
        self._search = value
        self.clear()

    def random(self) -> CebStatus:
        self._search = randint(100, 999)
        liste_plaques = LISTEPLAQUES[:]
        self._plaques[:] = []
        while len(self._plaques) < 6:
            valeur_plaque = randint(0, len(liste_plaques) - 1)
            self._plaques.append(CebPlaque(liste_plaques[valeur_plaque], self._observer))
            del liste_plaques[valeur_plaque]
        return self.clear()

    def json(self) -> str:
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
        return self._solutions \
            if self.status == CebStatus.CompteEstBon or self.status == CebStatus.CompteApproche else []

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
    def plaques(self, plq: List[int]):
        self._plaques[:] = [CebPlaque(k) for k in plq]
        self.clear()

    def valid(self) -> CebStatus:
        """
        validation du tirae
        :return : CebStatus
        """
        if not (99 < self._search < 1000):
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
            self._diff = diff
        elif sol not in self._solutions:
            self._solutions.append(sol)

    def resolve(self, plaques: List[int | CebPlaque] = (), search: int = 0) -> CebStatus:
        """

        :rtype: object
        """
        if search != 0 and len(plaques) == 6:
            self._search = search
            self.plaques = plaques

        if not self.auto:
            self.clear()
        if self._status == CebStatus.Invalide:
            return self._status
        self._status = CebStatus.EnCours
        self._resolve(self.plaques[:])
        self._solutions.sort(key=lambda sol: sol.rank)
        self.status = CebStatus.CompteEstBon \
            if self._solutions[0].value == self._search else CebStatus.CompteApproche
        return self._status

    async def resolve_async(self) -> CebStatus:
        return await asyncio.to_thread(self.resolve)

    def _resolve(self, lplaques: List) -> None:
        for i, plq in enumerate(lplaques):
            self._add_solution(plq)
            for j in range(i + 1, len(lplaques)):
                q = lplaques[j]
                for operation in "x+-/":
                    oper: CebOperation = CebOperation(plq, operation, q)
                    if oper.value != 0:
                        self._resolve([oper] +
                                      [x for k, x in enumerate(lplaques) if k not in (i, j)])

    @property
    def result(self) -> dict:
        return {
            "Search": self.search,
            "Plaques": [plq.value for plq in self._plaques],
            "Status": self._status.name,
            "Found": str(self.found),
            "Diff": self.diff,
            "Solutions": [str(sol) for sol in self.solutions]}

    def __repr__(self):
        return self.json

    @staticmethod
    def solve(plaques: List[int] = (), search: int = 0, auto: bool = False) -> CebTirage:
        _tirage = CebTirage(plaques, search, auto)
        _tirage.resolve()
        return _tirage


def resolve(plaques: List[int] = (), search: int = 0, auto: bool = False) -> CebTirage:
    return CebTirage.solve(plaques, search, auto)


if __name__ == "__main__":
    print()
    t = CebTirage(auto=False)
    t.resolve()
    print(f"search: {t.search}")
    print("plaques : ")
    for p in t.plaques:
        print(f"\t{p.value}")
    print("")
    match t.status:
        case CebStatus.CompteEstBon:
            print("Le Compte est bon")
        case CebStatus.CompteApproche:
            print(f"Compte approché: {t.found}")
        case CebStatus.Valide:
            print("Non calculé")
            exit(1)
        case _:
            print("Tirage invalide")
    print("")
    print(f"{t.count} solutions")
    for i, s in enumerate(t.solutions):
        print(f"\t{i}: \t{s}")
    print(len(t.solutions))
    t.plaques[0].value = 5
    print(len(t.solutions))
