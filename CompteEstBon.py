import argparse
import time

from PyCeb import CebTirage, CebStatus


def exec_time(fn):
    t = time.time()
    fn()
    return time.time() - t


print("#### Tirage du compte est bon#### ")
parser = argparse.ArgumentParser(description="Compte est bon")
parser.add_argument("-p", "--plaques", type=int,
                    nargs="+", help="plaques", default=[])
parser.add_argument("-s", "--search", dest="search",
                    help="Valeur à chercher", type=int, default=0)
args = parser.parse_args()

tirage = CebTirage(args.plaques, args.search)
print(f"Recherche: {tirage.search}", end=", ")
print("Tirage:", end=" ")
print(*tirage.plaques, sep=', ')
ti = exec_time(tirage.resolve)
print()

if tirage.status == CebStatus.COMPTEESTBON:
    print("Le Compte est bon")
elif tirage.status == CebStatus.ERREUR:
    print("Tirage invalide")
else:
    print("Compte approché: ", tirage.found)
print(f"Durée du calcul: {ti:.3f} s, nombre de solutions: {tirage.count}")
print(f"Nombre d'opérations: {tirage.noperations:> 20_}")
if tirage.count > 0:
    print("Solutions: ")
    for i, s in enumerate(tirage.solutions):
        print(f"{i + 1:4}: {s}")
