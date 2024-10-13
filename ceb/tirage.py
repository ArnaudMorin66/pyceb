"""
    Calcul du compte est bon
"""
from __future__ import annotations

import asyncio
import json
from builtins import list
from random import randint
from sys import maxsize
from typing import List

from ceb.base import CebBase
from ceb.iupdate import IUpdate
from ceb.operation import CebOperation
from ceb.plaque import CebPlaque, LISTEPLAQUES
from ceb.status import CebStatus


class CebTirage(IUpdate):
    """
    Tirage Plaques et Recherche
    """

    def __init__(
        self, plaques: List[int] = (), search: int = 0, auto: bool = False
    ) -> None:
        """

        @type search: int Valeur à chercher
        """
        super().__init__()
        self.auto: bool = auto
        self._plaques: List[CebPlaque] = []
        self._search: int = 0
        self._solutions: List[CebBase] = []
        self._diff: int = maxsize
        self._status: CebStatus = CebStatus.Indefini
        for k in plaques:
            self._plaques.append(CebPlaque(k, self))

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
        old = self._search
        self._search = value
        self.update(old, value)

    def random(self) -> CebStatus:
        self._search = randint(100, 999)
        liste_plaques = LISTEPLAQUES[:]
        self._plaques[:] = []
        while len(self._plaques) < 6:
            valeur_plaque = randint(0, len(liste_plaques) - 1)
            self._plaques.append(CebPlaque(liste_plaques[valeur_plaque], self))
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
        return (
            self._solutions
            if self.status in [CebStatus.CompteEstBon, CebStatus.CompteApproche] else []
        )

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
        if 100 <= self._search <= 999 and len(self._plaques) == 6:
            self._status = CebStatus.Valide
            for plaque in self._plaques:
                count_plaques: int = LISTEPLAQUES.count(plaque.value)
                if count_plaques == 0 or count_plaques < self._plaques.count(plaque):
                    self._status = CebStatus.Invalide
                    break
        else:
            self._status = CebStatus.Invalide
        return self._status

    def update(self, param1, param2):
        self.clear()

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

    def resolve(
        self, plaques: List[int | CebPlaque] = (), search: int = 0
    ) -> CebStatus:
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
        self.resolve_stack(self.plaques[:])
        self._solutions.sort(key=lambda sol: sol.rank)
        self.status = (
            CebStatus.CompteEstBon
            if self._solutions[0].value == self._search
            else CebStatus.CompteApproche
        )
        return self._status

    async def resolve_async(self) -> CebStatus:
        return await asyncio.to_thread(self.resolve)

    def resolve_stack(self, plaques: List) -> None:

        def next_list(current_list: List, ceb_operation: CebOperation, i:int, j: int)-> List:
            return [ceb_operation ]+[ x for k, x in enumerate(current_list) if k not in (i, j)]

        stack = [plaques]
        while stack:
            current_liste = stack.pop()
            for ix, plq in enumerate(current_liste):
                self._add_solution(plq)
                for jx in range(ix + 1, len(current_liste)):
                    q = current_liste[jx]
                    for operation in "x+-/":
                        oper: CebOperation = CebOperation(plq, operation, q)
                        if oper.value != 0:
                            next_liste =  next_list(current_liste, oper, ix, jx)
                            stack.append(next_liste)

    @property
    def result(self) -> dict:
        return {
            "Search": self.search,
            "Plaques": [plq.value for plq in self._plaques],
            "Status": self._status.name,
            "Found": str(self.found),
            "Diff": self.diff,
            "Solutions": [str(sol) for sol in self.solutions],
        }

    def __repr__(self):
        return self.json

    @staticmethod
    def solve(
        plaques: List[int] = (), search: int = 0, auto: bool = False
    ) -> CebTirage:
        _tirage = CebTirage(plaques, search, auto)
        _tirage.resolve()
        return _tirage


def resolve(plaques: List[int] = (), search: int = 0, auto: bool = False) -> CebTirage:
    return CebTirage.solve(plaques, search, auto)


if __name__ == "__main__":
    print("")
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
