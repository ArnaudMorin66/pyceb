from enum import Enum
from random import randint
from typing import List, Optional


class CebStatus(Enum):
    INDEFINI = 0,
    VALID = 1,
    ENCOURS = 2,
    COMPTEESTBON = 3,
    COMPTEAPPROCHE = 4,
    ERREUR = 5


MAXINT = 99999999


class CebBase:
    _value: int
    _operations: List[str]

    def __init__(self):
        self._value = 0
        self._operations = []

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

    def __repr__(self):
        return ", ".join(self._operations)


class CebPlaque(CebBase):
    def __init__(self, v):
        super().__init__()
        self._value = v
        self.operations.extend([str(v)])

    def __eq__(self, other):
        if not isinstance(other, CebPlaque):
            return False
        return self._value == other._value

    def __int__(self):
        return self._value


class CebOperation(CebBase):

    def __init__(self, g: CebBase, op: str, d: CebBase):
        super().__init__()
        if g._value < d._value:
            g, d = d, g
        self._eval(g, op, d)

    # @property
    def _eval(self, g: CebBase, op: str, d: CebBase):
        self._value = 0
        if op == "+":
            self._value = g._value + d._value
        elif op == "-":
            self._value = g._value - d._value
        elif op == "x":
            if g._value > 1 and d._value > 1:
                self._value = g._value * d._value
        elif op == "/":
            if d._value > 1:
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

    def __eq__(self, other: CebBase):
        """

        :type other: object
        """
        if isinstance(other, CebOperation):
            return self._operations == other.operations
        return False


class CebFind:
    def __init__(self):
        self._found1 = 0
        self._found2 = -1
        self.init(MAXINT)

    @property
    def found1(self):
        return self._found1

    @property
    def found2(self):
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
    def isunique(self):
        return self._found2 == -1

    def __repr__(self):
        if self.isunique:
            return str(self._found1)
        return f"{self._found1} et {self._found2}"

    def init(self, value: int):
        self._found1 = value
        self._found2 = -1


class CebTirage:
    listePlaques: List[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 25, 50, 75, 100,
                               1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 25]
    _diff: int
    _solutions: List[CebBase]
    _status: CebStatus
    _found: CebFind
    _search: int
    _nop: int
    _plaques: List[CebPlaque]

    def __init__(self):
        self._plaques = []
        self._search = 0
        self._found = CebFind()
        self._nop = 0
        self.rand()

    def clear(self):
        self._nop = 0
        self._solutions = []
        self._diff = MAXINT
        self._found.init(MAXINT)
        self.valid()

    @property
    def noperations(self) -> int:
        return self._nop

    @property
    def found(self):
        return self._found

    @property
    def search(self):
        return self._search

    @search.setter
    def search(self, value: int):
        self._search = value
        self.clear()

    def rand(self) -> CebStatus:
        self.clear()
        self._search = randint(100, 999)
        ll = self.listePlaques[:]
        self._plaques[:] = []

        while len(self._plaques) < 6:
            v = randint(0, len(ll) - 1)
            self._plaques.append(CebPlaque(ll[v]))
            del ll[v]
        self.valid()
        return self.status

    def _getstr(self) -> str:
        return "[" + "], [".join([", ".join(x.operations) for k, x in enumerate(self._solutions)]) + "]"

    @property
    def diff(self):
        return self._diff

    @property
    def count(self) -> int:
        return len(self.solutions)

    @property
    def solutions(self):
        return self._solutions

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def plaques(self):
        return self._plaques

    @plaques.setter
    def plaques(self, value: List[CebBase]):
        self._plaques[:] = []
        for p in value:
            if isinstance(p, int):
                self._plaques.append(CebPlaque(p))
            else:
                self._plaques.append(p)
        self.clear()

    def valid(self) -> CebStatus:
        if self._search < 100 or self._search > 999:
            self.status = CebStatus.ERREUR
            return self.status
        if len(self.plaques) > 6:
            self.status = CebStatus.ERREUR
            return self.status
        for p in self._plaques:
            kk = self.listePlaques.count(p.value)
            if self._plaques.count(p) > kk or kk == 0:
                self.status = CebStatus.ERREUR
                return self.status
        self.status = CebStatus.VALID
        return self.status

    @property
    def solution(self) -> Optional[CebBase]:
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

    def resolve_args(self, plaques: List[int], search: int) -> CebStatus:
        self._search = search
        self.plaques = plaques
        return self.resolve()

    def resolve(self) -> CebStatus:
        self.clear()
        if self.status == CebStatus.ERREUR:
            return self._status
        self._status = CebStatus.ENCOURS
        self._resolve(self.plaques[:])
        self._solutions.sort(key=lambda sol: sol.rank)
        if self.solutions[0].value == self._search:
            self.status = CebStatus.COMPTEESTBON
        else:
            self.status = CebStatus.COMPTEAPPROCHE
        return self._status

    def _resolve(self, plaq: List[CebBase]):
        """
        :type plaq: List[CebBase]
        """
        # pl: List[CebBase] = sorted(plaq, key=lambda p: p.value, reverse=True)
        for i, pi in enumerate(plaq):
            self._addsolution(pi)
            for j in range(i + 1, len(plaq)):
                pj = plaq[j]
                for op in ["x", "+", "/", "-"]:
                    re = CebOperation(pi, op, pj)
                    if re.value != 0:
                        self._resolve([x for k, x in enumerate(
                            plaq) if k != i and k != j] + [re])

    def __repr__(self):
        return f"Plaques: {self.plaques.__repr__()}, " \
               f"Recherche: {self.search.__repr__()}, Status: {str(self.status)}, " \
               f"Found: {self.found.__repr__()}, Nb solutions: {self.count.__repr__()}, " \
               f"Solutions: {self._getstr()}"
