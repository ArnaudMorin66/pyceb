from enum import Enum
from random import randint
from typing import List, Union


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
    _str: str
    _rank: int

    def __init__(self, v: int):
        self._value = v
        self._str = ""
        self._rank = 0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v: int):
        self._value = v

    @property
    def rank(self) -> int:
        return self._rank

    @property
    def str(self):
        return self._str

    def __str__(self):
        return self._str


class CebPlaque(CebBase):
    def __init__(self, v):
        super().__init__(v)
        self._str = str(v)
        self._rank = 1

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if not isinstance(other, CebPlaque):
            return False
        return self.value == other.value

    def __repr__(self):
        return str(self.value)

    def __int__(self):
        return self._value


class CebOperation(CebBase):

    def __init__(self, g: Union[CebBase, int], op: str, d: Union[CebBase, int]):
        super().__init__(0)
        if isinstance(g, int):
            g = CebPlaque(g)
        if isinstance(d, int):
            self._droite = CebPlaque(d)
        self._eval(g, op, d)

    # @property
    def _eval(self, g, op, d):
        self._value = 0
        if op == "+":
            self._value = g.value + d.value
        elif op == "-":
            if g.value > d.value:
                self._value = g.value - d.value
        elif op == "x":
            if g.value > 1 and d.value > 1:
                self._value = g.value * d.value
        elif op == "/":
            if d.value > 1:
                tmp = divmod(g.value, d.value)
                if tmp[1] == 0:
                    self._value =  tmp[0]
        self._str = ""
        if isinstance(g, CebOperation):
            self._str += g._str
        if isinstance(d, CebOperation):
            if self._str != "":
                self._str += ";"
            self._str += d._str
        if self._str != "":
            self._str += ";"
        self._str += f"{g.value} {op} {d.value} = {self._value}"
        self._rank = g._rank + d._rank

    def __eq__(self, other):
        return self._str == other.str

    def __repr__(self):
        return self._str


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

    def __str__(self):
        if self.isunique:
            return str(self._found1)
        return f"{self._found1} et {self._found2}"

    def __repr__(self):
        return str(self)

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
    _plaques: List[CebPlaque]

    def __init__(self):
        self._plaques = []
        self._search = 0
        self._found = CebFind()
        self.rand()

    def clear(self):
        self._solutions = []
        self._diff = MAXINT
        self._found.init(MAXINT)
        self.valid()

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

    def rand(self):
        self.clear()
        self._search = randint(100, 999)
        ll = self.listePlaques[:]
        self._plaques[:] = []
       
        while len(self._plaques) < 6:
            v = randint(0, len(ll) - 1)
            self._plaques.append(CebPlaque(ll[v]))
            del ll[v]
        self.valid()

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
    def plaques(self, value):
        self._plaques[:] = []
        for p in value:
            if isinstance(p, int):
                self._plaques.append(CebPlaque(p))
            else:
                self._plaques.append(p)
        self.clear()

    def valid(self):
        if self._search < 100 or self._search > 999:
            self.status = CebStatus.ERREUR
            return
        if len(self.plaques) > 6:
            self.status = CebStatus.ERREUR
            return
        for p in self._plaques:
            kk = self.listePlaques.count(p.value)
            if self._plaques.count(p) > kk or kk == 0:
                self.status = CebStatus.ERREUR
                return
        self.status = CebStatus.VALID

    @property
    def solution(self) -> Union[None, CebBase]:
        if self.count == 0:
            return None
        else:
            return self.solutions[0]

    def _addsolution(self, sol: CebBase):
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

    def resolve_args(self, plaques, search:int):
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

    def _resolve(self, plaq):
        pl: List[CebBase] = sorted(plaq, key=lambda p: p.value, reverse=True)
        for i, pi in enumerate(pl):
            self._addsolution(pi)
            for j in range(i + 1, len(pl)):
                pj = pl[j]
                for op in ["x", "+", "/", "-"]:
                    re = CebOperation(pi, op, pj)
                    if re.value != 0:
                        self._resolve([x for k, x in enumerate(pl) if k != i and k != j] + [re])

    def __repr__(self):
        return f"Plaques: {self.plaques}, Recherche: {self.search}, Status: {str(self.status)}, " \
               f"Found: {self.found}, Nb solutions: {self.count}, Solutions: {self.solutions}"
