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
    def __init__(self):
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
        """

        :type other: object
        """
        if isinstance(other, CebBase):
            return self._operations == other.operations
        return False


class CebPlaque(CebBase):
    def __init__(self, v=0):
        super().__init__()
        self._value = v
        self.operations.extend([str(v)])


class CebOperation(CebBase):

    def __init__(self, g: CebBase, op: str, d: CebBase):
        super().__init__()
        if g._value < d._value:
            g, d = d, g
        self._value = 0
        if op == "+":
            self._value = g._value + d._value
        elif op == "-":
            self._value = g._value - d._value
        elif op == "x":
            if g._value > 1 and d._value > 1:
                self._value = g._value * d._value
        elif op == "/":
            if d.value > 1:
                tmp = divmod(g._value, d._value)
                if tmp[1] == 0:
                    self._value = tmp[0]
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
        self._found1 = 0
        self._found2 = -1
        self.init(MAXINT)

    @property
    def found1(self) -> int:
        return self._found1

    @property
    def found2(self) -> int:
        return self._found2

    def add(self, value: int):
        if value == self._found1 or value == self._found2:
            return
        if value < self._found1:
            self._found2 = self._found1
            self._found1 = value
        else:
            self._found2 = value

    @property
    def isunique(self) -> bool:
        return self._found2 == -1

    def __repr__(self) -> str:
        if self.isunique:
            return str(self._found1)
        else:
            return f"{self._found1} et {self._found2}"

    def init(self, value: int):
        self._found1 = value
        self._found2 = -1


class CebTirage:
    ListePlaques: List[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 25, 50, 75, 100,
                               1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 25]
    PlaquesUniques = list(set(ListePlaques))

    # noinspection PyDefaultArgument
    def __init__(self, plaques: List[int] = (), search: int = 0):
        self._plaques: List[CebPlaque] = []
        for _, k in enumerate(plaques):
            self._plaques.append(CebPlaque(k))
        self._search: int = search
        self._found: CebFind = CebFind()
        self._solutions: List[CebBase] = []
        self._diff: int = MAXINT
        self._nop: int = 0
        self._status: CebStatus = CebStatus.INDEFINI
        if search != 0 or len(plaques) > 0:
            self.valid()
        else:
            self.rand()

    def clear(self) -> CebStatus:
        self._nop = 0
        self._solutions = []
        self._diff = MAXINT
        self._found.init(MAXINT)
        self.valid()
        return self.status

    @property
    def noperations(self) -> int:
        return self._nop

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
        ll = CebTirage.ListePlaques[:]
        self._plaques[:] = []
        for _ in range(6):
            v = randint(0, len(ll) - 1)
            self._plaques.append(CebPlaque(ll[v]))
            del ll[v]
        self.valid()

        return self.status

    def _getstr(self) -> str:
        return "{" + "}, {".join([", ".join(x.operations) for k, x in enumerate(self._solutions)]) + "}"

    @property
    def diff(self) -> int:
        return self._diff

    @property
    def count(self) -> int:
        return len(self.solutions)

    @property
    def solutions(self) -> List[CebBase]:
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
        if self._search < 100 or self._search > 999:
            self.status = CebStatus.ERREUR
            return self.status
        if len(self.plaques) > 6:
            self.status = CebStatus.ERREUR
            return self.status
        for p in self._plaques:
            kk = CebTirage.ListePlaques.count(p.value)
            if self._plaques.count(p) > kk or kk == 0:
                self.status = CebStatus.ERREUR
                return self.status
        self.status = CebStatus.VALID
        return self.status

    @property
    def solution(self) -> CebBase | None:
        if self.count == 0:
            return None
        else:
            return self.solutions[0]

    def _addsolution(self, sol: CebBase):
        self._nop += 1
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

    def resolve(self, plaques: List[int] = (), search: int = 0) -> CebTirage:
        """

        :rtype: object
        """
        if search != 0 and len(plaques) == 6:
            self._search = search
            self.plaques = plaques
        self.clear()
        if self.status == CebStatus.ERREUR:
            return self
        self._status = CebStatus.ENCOURS
        self._resolve(self.plaques[:])
        self._solutions.sort(key=lambda sol: sol.rank)
        if self.solutions[0].value == self._search:
            self.status = CebStatus.COMPTEESTBON
        else:
            self.status = CebStatus.COMPTEAPPROCHE
        return self

    def _resolve(self, plaq: List[CebBase]) -> None:
        """
        :type plaq: List[CebBase]
        """
        for i, pi in enumerate(plaq):
            self._addsolution(pi)
            for j in range(i + 1, len(plaq)):
                pj = plaq[j]
                for op in ["x", "+", "/", "-"]:
                    re = CebOperation(pi, op, pj)
                    if re.value != 0:
                        self._resolve([x for k, x in enumerate(
                            plaq) if k != i and k != j] + [re])

    @property
    def result(self):
        return self.status, self.found, self.solutions

    @property
    def data(self):
        return self.search, self.plaques

    def __repr__(self):
        return f"Plaques: {self.plaques.__repr__()}, " \
               f"Recherche: {self.search.__repr__()}, Status: {str(self.status)}, " \
               f"Found: {self.found.__repr__()}, Nb solutions: {self.count.__repr__()}, " \
               f"Solutions: {self._getstr()}"


if __name__ == "__main__":
    print(CebTirage().resolve())
