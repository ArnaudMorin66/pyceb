import argparse
import time

from PyCeb import CebTirage, CebStatus


def exec_time(fn) -> tuple:
    t = time.time()
    res = fn()
    return time.time() - t, res


print("#### Tirage du compte est bon#### ")
parser = argparse.ArgumentParser(description="Compte est bon")
parser.add_argument("-p", "--plaques", nargs="+",
                    type=int, help="plaques", default=[])
parser.add_argument("-s", "--search", dest="search",
                    help="Valeur à chercher", type=int, default=0)
args = parser.parse_args()

tirage = CebTirage(args.plaques, args.search)
print(f"Recherche: {tirage.search}", end=", ")
print("Tirage:", end=" ")
print(*tirage.plaques, sep=", ")
ti, status = exec_time(tirage.resolve)
print()
assert isinstance(ti, float)
assert isinstance(status, CebStatus)
match status:
    case CebStatus.COMPTEESTBON:
        print("Le Compte est bon")
    case CebStatus.COMPTEAPPROCHE:
        print("Compte approché: ", tirage.found)
    case _:
        print("Tirage invalide")

print(f"Durée du calcul: {ti:.3f} s, nombre de solutions: {tirage.count}")
print(f"Nombre d'opérations: {tirage.nb_operations:> 20_}")
if tirage.count > 0:
    print("Solutions: ")
    for i, s in enumerate(tirage.solutions):
        print(f"{i + 1:4} ({s.rank}): {s}")
