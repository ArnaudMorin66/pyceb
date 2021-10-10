from __future__ import annotations

from enum import Enum
from random import randint
from typing import List


class CebStatus(Enum):
    INDEFINI = 0,
    VALID = 1,
    ENCOURS = 2,
    COMPTEESTBON = 3,
    COMPTEAPPROCHE = 4,
    ERREUR = 5


MAXINT = 99999999


class CebBase:
    def __init__(self) -> None:
        self._value: int = 0
        self._operations: List[str] = []

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, v: int):
        self._value = v

    @property
    def rank(self) -> int:
        return len(self._operations)

    @property
    def operations(self) -> List[str]:
        return self._operations

    def __repr__(self) -> str:
        return ", ".join(self._operations)

    def __eq__(self, other: CebBase) -> bool:
        return self._operations == other.operations



class CebPlaque(CebBase):
    def __init__(self, v=0):
        super().__init__()
        self._value = v
        self.operations.extend([str(v)])


class CebOperation(CebBase):

    def __init__(self, g: CebBase, op: str, d: CebBase):
        """

        :type g: CebBase
        """
        super().__init__()
        if g._value < d._value:
            g, d = d, g
        self._value = 0

        match op:
            case "+":
                self._value = g._value + d._value
            case "-":
                self._value = g._value - d._value
            case "x":
                self._value = g._value * d._value if g._value > 1 and d._value > 1 else 0
            case "/":
                self._value = g._value // d._value if d._value > 1 and g._value % d._value == 0 else 0
        """
        if op == "+":
            self._value = g._value + d._value
        elif op == "-":
            self._value = g._value - d._value
        elif op == "x":
            self._value = g._value * d._value if g._value > 1 and d._value > 1 else 0
        elif op == "/":
            self._value = g._value // d._value if d._value <= 1 and g._value % d._value == 0 else 0
        """
        if self._value == 0:
            return
        self._operations.clear()
        if isinstance(g, CebOperation):
            self._operations.extend(g._operations)
        if isinstance(d, CebOperation):
            self.operations.extend(d.operations)
        self._operations.append(f"{g._value} {op} {d._value} = {self._value}")


class CebFind:
    def __init__(self):
        self._found1, self._found2 = 0, -1
        self.init(MAXINT)

    @property
    def found1(self) -> int:
        return self._found1

    @property
    def found2(self) -> int:
        return self._found2

    def add(self, value: int) -> None:
        if self._found1 == value or self._found2 == value:
            return
        if self._found1 > value:
            self._found2, self._found1 = self._found1, value
        else:
            self._found2 = value

    @property
    def isUnique(self) -> bool:
        return self._found2 == -1

    def __repr__(self) -> str:
        return str(self._found1) if self.isUnique else f"{self._found1} et {self._found2}"

    def init(self, value: int):
        self._found1, self._found2 = value, -1


LISTEPLAQUES: List[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 25, 50, 75, 100,
                           1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 25]
PLAQUESUNIQUES: list[int] = list(set(LISTEPLAQUES))


class CebTirage:

    def __init__(self, plaques: List[int] = (), search: int = 0) -> None:
        self._plaques: List[CebPlaque] = []
        if len(plaques) == 6:
            for _, k in enumerate(plaques):
                self._plaques.append(CebPlaque(k))
        self._search: int = search
        self._found: CebFind = CebFind()
        self._solutions: List[CebBase] = []
        self._diff: int = MAXINT
        self._nb_op: int = 0
        self._status: CebStatus = CebStatus.INDEFINI
        if search != 0 and len(plaques) > 0:
            self.valid()
        elif search == 0 and len(plaques) > 0:
            self._search = randint(100, 999)
            self.valid()
        else:
            self.rand()

    def clear(self) -> CebStatus:
        self._nb_op = 0
        self._solutions = []
        self._diff = MAXINT
        self._found.init(MAXINT)
        self.valid()
        return self.status

    @property
    def nb_operations(self) -> int:
        return self._nb_op

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

    def rand(self) -> CebStatus:
        self.clear()
        self._search = randint(100, 999)
        ll = LISTEPLAQUES[:]
        self._plaques[:] = []
        for _ in range(6):
            v = randint(0, len(ll) - 1)
            self._plaques.append(CebPlaque(ll[v]))
            del ll[v]
        self.valid()
        return self.status

    def _lststr(self) -> str:
        return "{" + "}, {".join([", ".join(x.operations) for _, x in enumerate(self._solutions)]) + "}"

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
        for p in value:
            if isinstance(p, int):
                self._plaques.append(CebPlaque(p))
            elif isinstance(p, CebPlaque):
                self._plaques.append(p)
            else:
                raise ValueError("Errur instance value")
        self.clear()

    def valid(self) -> CebStatus:
        if  self._search not in range(100,1000):
            self.status = CebStatus.ERREUR
            return self.status
        if len(self.plaques) > 6:
            self.status = CebStatus.ERREUR
            return self.status
        for p in self._plaques:
            kk = LISTEPLAQUES.count(p.value)
            if self._plaques.count(p) > kk or kk == 0:
                self.status = CebStatus.ERREUR
                return self.status
        self.status = CebStatus.VALID
        return self.status

    @property
    def solution(self) -> CebBase | None:
        return self.solutions[0] if self.count != 0 else None

    def _addsolution(self, sol: CebBase):
        self._nb_op += 1
        diff = abs(sol.value - self._search)
        if diff > self._diff:
            return
        if diff != self._diff:
            self._solutions = [sol]
            self._found.init(sol.value)
            self._diff = diff
        elif sol not in self._solutions:
            self._solutions.append(sol)
            self._found.add(sol.value)

    def resolve(self, plaques: List[int] = (), search: int = 0) -> CebStatus:
        """

        :rtype: object
        """
        if search != 0 and len(plaques) == 6:
            self._search = search
            self.plaques = plaques
        self.clear()
        if self.status == CebStatus.ERREUR:
            return self.status
        self._status = CebStatus.ENCOURS
        self._resolve(self.plaques[:])
        self._solutions.sort(key=lambda sol: sol.rank)
        self.status = CebStatus.COMPTEESTBON if self.solutions[0].value == self._search else CebStatus.COMPTEAPPROCHE
        return self.status

    def _resolve(self, plaq: List[CebBase]) -> None:
        """
        :rtype: None
        :type plaq: List[CebBase]
        """
        for i, pi in enumerate(plaq):
            self._addsolution(pi)
            for j in range(i + 1, len(plaq)):
                pj = plaq[j]
                for op in "x+/-":
                    oper = CebOperation(pi, op, pj)
                    if oper.value != 0:
                        self._resolve([oper] + [x for k, x in enumerate(plaq) if k != i and k != j])

    @property
    def result(self) -> tuple:
        return self.status, self.found, self.solutions

    @property
    def data(self) -> tuple:
        return self.search, self.plaques

    def __str__(self):
        return f"Plaques: {self.plaques}, " \
               f"Recherche: {self.search}, " \
               f"Status: {str(self.status)}, " \
               f"Found: {self.found}, " \
               f"Nb solutions: {self.count}, " \
               f"Solutions: {self._lststr()} "


def solve_ceb(plaques: List[int], search: int) -> CebTirage | CebStatus:
    t = CebTirage(plaques, search)
    t.resolve()
    return t if t.status != CebStatus.ERREUR else CebStatus.ERREUR


if __name__ == "__main__":
    tirage = CebTirage()
    re = tirage.resolve()
    for s in enumerate(tirage.solutions):
        print(tirage.solutions)
