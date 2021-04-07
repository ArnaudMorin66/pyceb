import argparse
import time
import PyCeb

print("#### Tirage du compte est bon#### ")
parser = argparse.ArgumentParser(description="Compte est bon")
parser.add_argument("-p", "--plaques", type=int, nargs="+", help="plaques", default=[])
parser.add_argument("-s", "--search", dest="search",
                    help="Valeur à chercher", type=int, default=0)
args = parser.parse_args()

tirage = PyCeb.CebTirage(args.search, args.plaques)
# if args.search is not None:
#    tirage.search = args.search
# if args.plaques is not None:
#     tirage.plaques = args.plaques[0:6]
print(f"Recherche: {tirage.search}", end=", ")
print("Tirage:", end=" ")
print(*tirage.plaques, sep=',')
ti = time.time()
tirage.resolve()
ti = time.time() - ti
print()
if tirage.status == PyCeb.CebStatus.COMPTEESTBON:
    print("Le Compte est bon")
elif tirage.status == PyCeb.CebStatus.ERREUR:
    print("Tirage invalide")
else:
    print("Compte approché: ", tirage.found)
print(f"Durée du calcul: {ti} s, nombre de solutions: {tirage.count}")
print(f"Nombre d'opérations: {tirage.noperations}")
if tirage.count > 0:
    print("Solutions: ")
    print(*tirage.solutions, sep='\n')
