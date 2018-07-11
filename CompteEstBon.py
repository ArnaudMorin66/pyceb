from random import randint
from enum import Enum


class CebStatus(Enum):
    INDEFINI = 0,
    VALID = 1,
    ENCOURS = 2,
    COMPTEESTBON = 3,
    COMPTEAPPROCHE = 4,
    ERREUR = 5


class CebBase:
    def __init__(self, v):
        self._value = v

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v


class CebPlaque (CebBase):
    def __init__(self, v):
        super().__init__(v)
        # self.value = v

    def __str__(self):
        return str(self.value)

    @property
    def path(self):
        return 1


class CebOperation(CebBase):
    def __init__(self, g, op, d):
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
    def gauche(self):
        return self._gauche

    @gauche.setter
    def gauche(self, v):
        self._gauche = v

    @property
    def droite(self):
        return self._droite

    @droite.setter
    def droite(self, v):
        self._droite = v

    @property
    def operation(self):
        return self._operation

    @operation.setter
    def operation(self, v):
        self._operation = v

    @property
    def path(self):
        return self.gauche.path + self.droite.path

    def __eq__(self, other):
        if not isinstance(other, CebOperation):
            return False
        if self._value != other.value:
            return False
        if self._operation != other.operation:
            return False
        if self.gauche == other.gauche and self.droite == other.droite:
            return True
        if self.gauche == other.droite and self.droite == other.gauche:
            return True
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


listePlaques = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 25, 50, 75, 100,
                1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 25]


class CebFind:
    def __init__(self):
        self._found1 = 0
        self._found2 = -1
        self.Init(999999)

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

        return format("{} et {}", self._found1, self._found2)

    def __repr__(self):
        return str(self)

    def Init(self, value):
        self._found1 = value
        self._found2 = -1


class CebTirage:
    def __init__(self):
        self._plaques = []
        self._search = 0
        self._found = CebFind()
        self._status = CebStatus.VALID
        self._solutions = []
        self._diff = 9999999
        self.rand()

    def clear(self):
        self._solutions = []
        self._found.Init(99999999)

    @property
    def found(self):
        return self._found

    @property
    def search(self):
        return self._search

    def rand(self):
        self._search = randint(100, 999)
        ll = listePlaques[:]
        self._plaques[:] = []
        for i in range(0, 6):
            v = randint(0, len(ll)-1)
            self._plaques.append(CebPlaque(ll[v]))
            del ll[v]

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

    def addsolution(self, s):
        diff = abs(s.value - self._search)
        if diff > self._diff:
            return
        if diff != self._diff:
            self._solutions = [s]
            self._found.Init(s.value)
            self._diff = diff
            return
        for sl in self._solutions:
            if s == sl:
                return
        self._solutions.append(s)
        self._found.add(s.value)

    def resolve_args(self, search, plaques):
        self.clear()
        self._search = search
        self.plaques = plaques
        self.resolve()

    def resolve(self):
        self.clear()
        self._resolve(self.plaques[:])
        self._solutions.sort(key=lambda s: s.path)

    def _resolve(self, plaq):
        pl = sorted(plaq, key=lambda p: p.value, reverse=True)
        for i in range(0, len(pl)):
            self.addsolution(pl[i])
            for j in range(i+1, len(pl)):
                for op in ["x", "+", "/", "-"]:
                    re = CebOperation(pl[i], op, pl[j])
                    if re.value != 0:
                        ls = [re]
                        for k in range(0, len(pl)):
                            if k != i and k != j:
                                ls.append(pl[k])
                        self._resolve(ls)


if __name__ == "__main__":
    tirage = CebTirage()
    tirage.resolve_args(234, [1, 3, 5, 7, 9, 25])
    print("Trouvé: {}, Nombre de solutions: {}".format(tirage.found, len(tirage.solutions)))
    for s in tirage.solutions:
        print("path: {}, solution: {}".format(s.path, s))
