import argparse
from json import load
import os
import pickle
import sys
import tempfile
import time
from datetime import datetime
from argparse import ArgumentParser
from zipfile import ZipFile, ZIP_LZMA
from ceb import CebTirage, CebStatus
from pymongo import MongoClient, database


def export_to_mongodb(server: str, tir: CebTirage):
    client: MongoClient = MongoClient(server)
    db: database = client.ceb
    domaine: str = os.getenv("USERDOMAIN" if sys.platform == "win32" else "HOST")
    db.comptes.insert_one({"_id": {"lang": "python", "domain": domaine, "date": datetime.utcnow()}} | tir.result)


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
parser.add_argument("-S", "--save", dest="save_data", type=bool,
                    action=argparse.BooleanOptionalAction,
                    help="Sauvegarde du tirage", default=None)
args = parser.parse_args()

tirage: CebTirage = CebTirage()

if args.plaques:
    tirage.plaques = args.plaques

if args.search != 0:
    tirage.search = args.search

if len(args.integers) > 5:
    if args.integers[0] > 100:
        tirage.search = args.integers[0]
        tirage.plaques = args.integers[1:]
    else:
        tirage.plaques = args.integers[0:6]
        if len(args.integers) > 6:
            tirage.search = args.integers[6]

if args.extract_json:
    tirage.resolve()
    print(tirage.to_json())
else:
    print("#### Tirage du compte est bon ####")
    print("Tirage:", end=" ")
    print(*tirage.plaques, sep=", ", end="\t")
    print(f"Recherche: {tirage.search}")

    # timer: int = time.perf_counter_ns()
    timer: int = time.process_time_ns()
    status: CebStatus = tirage.resolve()
    ellapsed: int = time.process_time_ns() - timer
    print()

    # noinspection PyCompatibility
    match status:
        case CebStatus.CompteEstBon:
            print("Le Compte est bon", end=", ")
        case CebStatus.CompteApproche:
            print(f"Compte approché: {tirage.found}", end=", ")
        case _:
            print("Tirage invalide", end=", ")

    print(f"nombre de solutions trouvées: {tirage.count}", end=", ")
    print(f"Durée du calcul: {ellapsed / 1.E+09: 0.3f} s")
    if tirage.count > 0:
        print("\nSolutions:")
        for i, s in enumerate(tirage.solutions):
            print(f"{i + 1:4}/{tirage.count:4} ({s.rank:1}), {tirage.status.name}: {s}")
    print()
# recherche fichier

match sys.platform:
    case "win32":
        user_profile = os.getenv("USERPROFILE")
        cible = rf"{user_profile}\AppData\Local\Ceb"
        file_config = rf"{cible}\config.json"
    case "linux":
        user_profile = os.getenv("HOME")
        cible = f"{user_profile}/.local/ceb"
        file_config = f"{cible}/config.json"
    case _:
        raise "OS Inconnu"
if not os.path.isdir(cible):
    os.mkdir(cible)

if not os.path.exists(file_config):
    sys.exit(0)

with open(file_config, mode="r", encoding="utf-8") as fp:
    config = load(fp)

if config["mongodb"]:
    export_to_mongodb(config["mongodbserver"], tirage)

match args.save_data:
    case None:
        save = config["save"]
        if not save:
            sys.exit(0)
    case False:
        sys.exit(0)

zipfile = config[sys.platform]["zipfile"]
if zipfile != "":
    with ZipFile(zipfile, mode="a", compression=ZIP_LZMA) as fzip:
        num = max([0] + [int(g) for g in [f[0:f.rfind(".")] for f in fzip.namelist()] if g.isdigit()]) + 1
        jsonfile = f"{num:06}.json"
        fzip.writestr(jsonfile, tirage.to_json())
        pick = config["pickfile"]
        if pick:
            num += 1
            pklfile = f"{num:06}.pkl"
            pickfile = tempfile.NamedTemporaryFile(mode="w+b", prefix="ceb_", suffix=".tmp", delete=False)
            pickle.dump(tirage.result, pickfile)
            pickfile.close()
            fzip.write(pickfile.name, pklfile)
            os.remove(pickfile.name)
