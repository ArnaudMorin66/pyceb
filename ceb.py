from enum import Enum
from random import randint
import time
import argparse
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
    _value: int

    def __init__(self, v: int):
        self._value = v

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v: int):
        self._value = v

    @property
    def path(self) -> int:
        return 0


class CebPlaque(CebBase):
    def __init__(self, v):
        super().__init__(v)
        # self.value = v

    def __str__(self):
        return str(self.value)

    @property
    def path(self) -> int:
        return 1

    def __eq__(self, other):
        if not isinstance(other, CebPlaque):
            return False
        return self.value == other.value

    def __repr__(self):
        return str(self.value)


class CebOperation(CebBase):
    _gauche: CebBase
    _droite: CebBase
    _operation: str

    def __init__(self, g: CebBase, op: str, d: CebBase):
        super().__init__(0)
        if isinstance(g, int):
            self._gauche = CebPlaque(g)
        else:
            self._gauche = g
        self._operation = op
        if isinstance(d, int):
            self._droite = CebPlaque(d)
        else:
            self._droite = d
        self.value = self.calc()

    def calc(self):
        if self._operation == "+":
            return self._gauche.value + self._droite.value
        if self._operation == "-":
            if self._gauche.value < self._droite.value:
                return 0
            return self._gauche.value - self._droite.value
        if self._operation == "x":
            if self._gauche.value <= 1 or self._droite.value <= 1:
                return 0
            return self._gauche.value * self._droite.value
        if self._operation == "/":
            if self._droite.value <= 1:
                return 0
            if self._gauche.value % self._droite.value != 0:
                return 0
            return self._gauche.value // self._droite.value
        return 0

    @property
    def gauche(self) -> CebBase:
        return self._gauche

    @gauche.setter
    def gauche(self, v):
        self._gauche = v

    @property
    def droite(self) -> CebBase:
        """

        :rtype: int
        """
        return self._droite

    @droite.setter
    def droite(self, v):
        self._droite = v

    @property
    def operation(self) -> str:
        return self._operation

    @operation.setter
    def operation(self, v):
        self._operation = v

    @property
    def path(self) -> int:
        return self.gauche.path + self.droite.path

    def __eq__(self, other):
        if str(self) == str(other):
            return True
        else:
            return False

    def __str__(self):
        result = ""
        if isinstance(self.gauche, CebOperation):
            result += str(self.gauche)
        if isinstance(self.droite, CebOperation):
            if result != "":
                result += ", "
            result += str(self.droite)
        if result != "":
            result += ", "
        result += "{} {} {} = {}".format(self.gauche.value,
                                         self.operation, self.droite.value, self.value)
        return result

    def __repr__(self):
        return str(self)


listePlaques = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 25, 50, 75, 100,
                1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 25]


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

    def add(self, value):
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
        return "{} et {}".format(self._found1, self._found2)

    def __repr__(self):
        return str(self)

    def init(self, value):
        self._found1 = value
        self._found2 = -1


class CebTirage:
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
    def search(self, value):
        self._search = value
        self.clear()

    def rand(self):
        self.clear()
        self._search = randint(100, 999)
        ll = listePlaques[:]
        self._plaques[:] = []
        for ix in range(0, 6):
            v = randint(0, len(ll) - 1)
            self._plaques.append(CebPlaque(ll[v]))
            del ll[v]

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

    def addsolution(self, sol: CebBase):
        diff = abs(sol.value - self._search)
        if diff > self._diff:
            return
        if diff != self._diff:
            self._solutions = [sol]
            self._found.init(sol.value)
            self._diff = diff
            return
        if sol in self._solutions:
            return
        self._solutions.append(sol)
        self._found.add(sol.value)

    def resolve_args(self, search, plaques):
        self._search = search
        self.plaques = plaques
        return self.resolve()

    def resolve(self):
        self.clear()
        if self.status == CebStatus.ERREUR:
            return
        self._status = CebStatus.ENCOURS
        self._resolve(self.plaques[:])
        self._solutions.sort(key=lambda sol: sol.path)
        if self.solutions[0].value == self._search:
            self.status = CebStatus.COMPTEESTBON
        else:
            self.status = CebStatus.COMPTEAPPROCHE
        return self._status

    def valid(self):
        if self._search < 100 or self._search > 999:
            self.status = CebStatus.ERREUR
            return
        if len(self.plaques) > 6:
            self.status = CebStatus.ERREUR
            return
        for v in self._plaques:
            n = self._plaques.count(v)
            kk = listePlaques.count(v.value)
            if n > kk or kk == 0:
                self.status = CebStatus.ERREUR
                return
        self.status = CebStatus.VALID

    @property
    def solution(self) -> CebBase:
        if self.count == 0:
            return None
        else:
            return self.solutions[0]

    def _resolve(self, plaq):
        pl = sorted(plaq, key=lambda p: p.value, reverse=True)
        for ix in range(0, len(pl)):
            self.addsolution(pl[ix])
            for j in range(ix + 1, len(pl)):
                for op in ["x", "+", "/", "-"]:
                    re = CebOperation(pl[ix], op, pl[j])
                    if re.value != 0:
                        ls = [re]
                        for k in range(0, len(pl)):
                            if k != ix and k != j:
                                ls.append(pl[k])
                        self._resolve(ls)


if __name__ == "__main__":
    def main():
        tirage = CebTirage()
        parser = argparse.ArgumentParser(description="Compte est bon")
        parser.add_argument("-p", "--plaques", type=int, nargs="+", help="plaques")
        parser.add_argument("-s", "--search", dest="search", help="Valeur", type=int)
        args = parser.parse_args()
        if args.search is not None:
            tirage.search = args.search
        if args.plaques is not None:
            tirage.plaques = args.plaques[0:6]
        ti = time.time()
        tirage.resolve()
        ti = time.time() - ti
        print("#### Tirage du compte est bon#### ")
        print("Recherche: {}".format(tirage.search), end=", ")
        print("Tirage:", end=" ")
        for pp in tirage.plaques:
            print(pp.value, end=" ")
        print()
        if tirage.status == CebStatus.COMPTEESTBON:
            print("Le Compte est bon")
        elif tirage.status == CebStatus.ERREUR:
            print("Tirage invalide")
        else:
            print("Compte approché: ", tirage.found)
        print("Durée du calcul: {} s, nombre de solutions: {}".format(ti, tirage.count))
        if tirage.count > 0:
            print("Solutions: ")
            for s in tirage.solutions:
                print(s)
    main()