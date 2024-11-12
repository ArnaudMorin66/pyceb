# .\venv\Scripts\python.exe
""" Tirage du Compte est bon """
import os
import pickle
import sys
import tempfile
import time
from argparse import ArgumentParser, BooleanOptionalAction
from json import load
from typing import Callable
from zipfile import ZipFile, ZIP_LZMA

import keyboard

from ceb import CebTirage, CebStatus


def exec_time(fun: Callable, *vals: object) -> tuple[int, any]:  # type: ignore
    """
    execute la fonction fn avec les paramètres vals
    @rtype: object
    @type fun: object
    """
    timer: int = time.process_time_ns()
    result = fun(*vals)
    return time.process_time_ns() - timer, result


wait: bool = False
parser: ArgumentParser = ArgumentParser(description="Compte est bon")
parser.add_argument("-p", "--plaques", nargs="+", type=int, help="plaques", default=[])
parser.add_argument(
    "-s", "--search", dest="search", help="Valeur à chercher", type=int, default=0
)
# noinspection PyTypeChecker
parser.add_argument(
    "-j",
    "--json",
    dest="extract_json",
    action=BooleanOptionalAction,
    type=bool,
    help="affichage du tirage",
    default=False,
)
# noinspection PyTypeChecker
parser.add_argument(
    "-w",
    "--wait",
    dest="wait",
    type=bool,
    action=BooleanOptionalAction,
    help="attendre retour",
    default=False,
)
parser.add_argument(
    "integers", metavar="N", type=int, nargs="*", help="plaques & valeur à chercher"
)
# noinspection PyTypeChecker
parser.add_argument(
    "-S",
    "--save",
    dest="save_data",
    type=bool,
    action=BooleanOptionalAction,
    help="Sauvegarde du tirage",
    default=None,
)
args = parser.parse_args()

tirage: CebTirage = CebTirage()

if args.plaques:
    # noinspection PyBroadException
    try:
        tirage.plaques = args.plaques
    except:
        print("Plaques invalide")
        exit(10)

if args.search != 0:
    tirage.search = args.search

if len(args.integers) > 0:
    if args.integers[0] > 100:
        tirage.search = args.integers[0]
        if len(args.integers) > 1:
            tirage.plaques = args.integers[1:7]
    else:
        tirage.plaques = args.integers[0:6]
        if len(args.integers) > 6:
            tirage.search = args.integers[6]

if args.extract_json:
    tirage.resolve()
    print(tirage.json)
else:
    print("#### Tirage du compte est bon ####")
    print("Tirage:", end=" ")
    print(*tirage.plaques, sep=", ", end="\t")
    print(f"Recherche: {tirage.search}")

    ellapsed: int
    status: CebStatus
    ellapsed, status = exec_time(tirage.resolve)  # time.process_time_ns() - timer
    print()

    # noinspection PyCompatibility
    match status:
        case CebStatus.CompteEstBon:
            print(f"Le Compte est bon", end=", ")
        case CebStatus.CompteApproche:
            print(f"Compte approché: {tirage.found}", end=", ")
        case _:
            print("Tirage invalide", end=", ")

    print(f"nombre de solutions trouvées: {tirage.count}", end=", ")
    print(f"Durée du calcul: {ellapsed / 1.E+09: 0.3f} s")
    if tirage.count > 0:
        print("\nSolutions:")
        for i, s in enumerate(tirage.solutions):
            print(f" {i + 1}/{tirage.count} ({s.rank}) {"$" if tirage.status == CebStatus.CompteEstBon else "~"} {s}")
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
        raise Exception(f"Platform Inconnu: {sys.platform}")

if not os.path.isdir(cible):
    os.mkdir(cible)

if os.path.exists(file_config):
    with open(file_config, mode="r", encoding="utf-8") as fp:
        config = load(fp)
    sauvegarde: bool = True
    match args.save_data:
        case None:
            save = config["save"]
            if not save:
                sauvegarde = False
        case False:
            # noinspection PyRedeclaration
            sauvegarde = False
        case _:
            # noinspection PyRedeclaration
            sauvegarde = True

    if sauvegarde:
        zipfile = config[sys.platform]["zipfile"]
        if zipfile != "":
            with ZipFile(zipfile, mode="a", compression=ZIP_LZMA) as fzip:
                num = (
                        max(
                            [0]
                            + [
                                int(g)
                                for g in [f[0: f.rfind(".")] for f in fzip.namelist()]
                                if g.isdigit()
                            ]
                        )
                        + 1
                )
            jsonfile = f"{num: 06}.json"
            fzip.writestr(jsonfile, tirage.json)
            pick = config["pickfile"]
            if pick:
                num += 1
                pklfile = f"{num: 06}.pkl"
                pickfile = tempfile.TemporaryFile(
                    prefix="ceb_", suffix=".tmp", delete=False
                )
                # noinspection PyTypeChecker
                pickle.dump(tirage.result, pickfile)
                pickfile.close()
                fzip.write(pickfile.name, pklfile)
                # os.remove(pickfile.name)
print("<FINI>")
if args.wait:
    print("(q) pour finir", end="\n")
    while not keyboard.is_pressed("q"):
        continue
else:
    print("\n")
