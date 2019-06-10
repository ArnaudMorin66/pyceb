import argparse
import time
from PyCeb import CebTirage, CebStatus

parser = argparse.ArgumentParser(description="Compte est bon")
parser.add_argument("-p", "--plaques", type=int, nargs="+", help="plaques")
parser.add_argument("-s", "--search", dest="search", help="Valeur à chercher", type=int)
args = parser.parse_args()
tirage = CebTirage()
if args.search is not None:
    tirage.search = args.search
if args.plaques is not None:
    tirage.plaques = args.plaques[0:6]
ti = time.time()
tirage.resolve()
ti = time.time() - ti
print("#### Tirage du compte est bon#### ")
print(f"Recherche: {tirage.search}", end=", ")
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
print(f"Durée du calcul: {ti} s, nombre de solutions: {tirage.count}")
if tirage.count > 0:
    print("Solutions: ")
    for s in tirage.solutions:
        print(s)
