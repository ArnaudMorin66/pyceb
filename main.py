import argparse
import time
import pickle
from PyCeb import *

print("#### Tirage du compte est bon#### ")
parser = argparse.ArgumentParser(description="Compte est bon")
parser.add_argument("-p", "--plaques", type=int, nargs="+", help="plaques")
parser.add_argument("-s", "--search", dest="search",
                    help="Valeur à chercher", type=int)
args = parser.parse_args()
tirage = CebTirage()
if args.search is not None:
    tirage.search = args.search
if args.plaques is not None:
    tirage.plaques = args.plaques[0:6]
print(f"Recherche: {tirage.search}", end=", ")
print("Tirage:", end=" ")
print(*tirage.plaques, sep=',')
ti = time.time()
tirage.resolve()
ti = time.time() - ti
print()
if tirage.status == CebStatus.COMPTEESTBON:
    print("Le Compte est bon")
elif tirage.status == CebStatus.ERREUR:
    print("Tirage invalide")
else:
    print("Compte approché: ", tirage.found)
print(f"Durée du calcul: {ti} s, nombre de solutions: {tirage.count}")
print(f"Nombre d'opérations: {tirage.noperations}")
if tirage.count > 0:
    print("Solutions: ")
    print(*tirage.solutions, sep='\n')
with open("tirage.data", "wb") as fs:
    p = pickle.Pickler(fs)
    p.dump(tirage)
    # fs.write(pickle.dumps(tirage))
with open("tirage.data", "rb") as fr:
    data: CebTirage = pickle.loads(fr.read())
print(data)
data.rand()
data.resolve()
print(*data.solutions, sep="\n")
