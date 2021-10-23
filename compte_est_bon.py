import argparse
import json
import os
import time
from argparse import ArgumentParser
from zipfile import ZipFile, ZIP_LZMA
from pyceb import CebTirage, CebStatus

parser: ArgumentParser = argparse.ArgumentParser(description="Compte est bon")
parser.add_argument("-p", "--plaques", nargs="+",
                    type=int, help="plaques", default=[])
parser.add_argument("-s", "--search", dest="search",
                    help="Valeur à chercher", type=int, default=0)
parser.add_argument("-j", "--json", dest="extract_json", type=bool,
                    action=argparse.BooleanOptionalAction,
                    help="affichage du tirage", default=False)
parser.add_argument('integers', metavar='N', type=int, nargs='*',
                    help='plaques & valeur à chercher')
args = parser.parse_args()

tirage: CebTirage = CebTirage()

if args.plaques:
    tirage.plaques = args.plaques

if args.search != 0:
    tirage.search = args.search

if len(args.integers) > 5:
    tirage.plaques = args.integers[0:6]
    if len(args.integers) > 6:
        tirage.search = args.integers[6]

if args.extract_json:
    tirage.resolve()
    print(tirage.to_json())
else:
    print("#### Tirage du compte est bon#### ")
    print("Tirage:", end=" ")
    print(*tirage.plaques, sep=", ", end="\t")
    print(f"Recherche: {tirage.search}")

    timer: int = time.perf_counter_ns()
    status: CebStatus = tirage.resolve()
    ellapsed: int = time.perf_counter_ns() - timer
    print()

    # noinspection PyCompatibility
    match status:
        case CebStatus.COMPTEESTBON:
            print("Le Compte est bon", end=", ")
        case CebStatus.COMPTEAPPROCHE:
            print(f"Compte approché: {tirage.found}", end=", ")
        case _:
            print("Tirage invalide", end=", ")

    print(f"nombre de solutions trouvées: {tirage.count}", end=", ")
    print(f"Durée du calcul: {ellapsed / 1.E+09: 0.3f} s")
    if tirage.count > 0:
        print("\nSolutions:")
        for i, s in enumerate(tirage.solutions):
            print(f"{tirage.status.name}:{i + 1:04}({s.rank:01}): {s}")
    print()
# recherche fichier
cible = rf"{os.getenv('USERPROFILE')}\AppData\Local\\Ceb"
if not os.path.isdir(cible):
    os.mkdir(cible)
config = rf"{cible}\config.json"

if os.path.exists(config):
    zip_file = ""
    with open(config, encoding="utf-8") as fp:
        jconf = json.load(fp)
        zip_file = jconf["Ceb"]["ZipFile"]
    if zip_file != "":
        with ZipFile(zip_file, mode="a", compression=ZIP_LZMA) as fzip:
            num = "1.json"
            if len(fzip.namelist()) > 0:
                num = f"{int(max([int(fn.split('.')[0]) for fn in fzip.namelist()])) + 1}.json"
            fzip.writestr(num, tirage.to_json())
