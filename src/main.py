# .\venv\Scripts\python.exe
"""
Tirage du Compte est bon
"""
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


def exec_time(fun: Callable, *vals: object) -> tuple[int, any]:
    """
    Mesure le temps d'exécution d'une fonction.

    Args:
        fun (Callable): La fonction à exécuter.
        *vals (object): Les arguments de la fonction.

    Returns:
        tuple[int, any]: Le temps d'exécution en nanosecondes et le résultat de la fonction.
    """
    timer: int = time.process_time_ns()
    result = fun(*vals)
    return time.process_time_ns() - timer, result


class CompteEstBon:
    """
    Classe principale pour le jeu du Compte est bon.
    """
    def __init__(self):
        """
        Initialise les arguments de la ligne de commande et le tirage.
        """
        self.wait = False
        self.parser = ArgumentParser(description="Compte est bon")
        self.parser.add_argument("-p", "--plaques", nargs="+", type=int, help="plaques", default=[])
        self.parser.add_argument("-s", "--search", dest="search", help="Valeur à chercher", type=int, default=0)
        self.parser.add_argument("-j", "--json", dest="extract_json", action=BooleanOptionalAction, type=bool, help="affichage du tirage", default=False)
        self.parser.add_argument("-w", "--wait", dest="wait", type=bool, action=BooleanOptionalAction, help="attendre retour", default=False)
        self.parser.add_argument("integers", metavar="N", type=int, nargs="*", help="plaques & valeur à chercher")
        self.parser.add_argument("-S", "--save", dest="save_data", type=bool, action=BooleanOptionalAction, help="Sauvegarde du tirage", default=None)
        self.args = self.parser.parse_args()
        self.tirage = CebTirage()

    def configure_tirage(self):
        """
        Configure le tirage en fonction des arguments de la ligne de commande.
        """
        if self.args.plaques:
            # noinspection PyBroadException
            try:
                self.tirage.plaques = self.args.plaques
            except:
                print("Plaques invalide")
                sys.exit(1)

        if self.args.search != 0:
            self.tirage.search = self.args.search

        if len(self.args.integers) > 0:
            if self.args.integers[0] > 100:
                self.tirage.search = self.args.integers[0]
                if len(self.args.integers) > 1:
                    self.tirage.plaques = self.args.integers[1:7]
            else:
                self.tirage.plaques = self.args.integers[0:6]
                if len(self.args.integers) > 6:
                    self.tirage.search = self.args.integers[6]

    def display_tirage(self):
        """
        Affiche le tirage et les résultats du calcul.
        """
        if self.args.extract_json:
            self.tirage.resolve()
            print(self.tirage.json)
        else:
            print("#### Tirage du compte est bon ####")
            print("Tirage:", end=" ")
            print(*self.tirage.plaques, sep=", ", end="\t")
            print(f"Recherche: {self.tirage.search}")

            ellapsed, status = exec_time(self.tirage.resolve)
            print()

            match status:
                case CebStatus.CompteEstBon:
                    print(f"Le Compte est bon", end=", ")
                case CebStatus.CompteApproche:
                    print(f"Compte approché: {self.tirage.found}", end=", ")
                case _:
                    print("Tirage invalide", end=", ")

            print(f"nombre de solutions trouvées: {self.tirage.count}", end=", ")
            print(f"Durée du calcul: {ellapsed / 1.E+09: 0.3f} s")
            if self.tirage.count > 0:
                print("\nSolutions:")
                for i, s in enumerate(self.tirage.solutions):
                    print(f" {i + 1}/{self.tirage.count} ({s.rank}) {'$' if self.tirage.status == CebStatus.CompteEstBon else '~'} {s}")
            print()
            print()

    def search_file(self):
        """
        Recherche et sauvegarde les fichiers de configuration et de résultats.
        """
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
            sauvegarde = True
            match self.args.save_data:
                case None:
                    save = config["save"]
                    if not save:
                        sauvegarde = False
                case False:
                    sauvegarde = False
                case _:
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
                    fzip.writestr(jsonfile, self.tirage.json)
                    pick = config["pickfile"]
                    if pick:
                        num += 1
                        pklfile = f"{num: 06}.pkl"
                        pickfile = tempfile.TemporaryFile(prefix="ceb_", suffix=".tmp", delete=False)
                        pickle.dump(self.tirage.result, pickfile)
                        pickfile.close()
                        fzip.write(pickfile.name, pklfile)

    def run(self):
        """
        Exécute le programme principal.
        """
        self.configure_tirage()
        self.display_tirage()
        self.search_file()
        print("<FINI>")
        if self.args.wait:
            print("(q) pour finir", end="\n")
            while not keyboard.is_pressed("q"):
                continue
        else:
            print("\n")
        return 0

if __name__ == "__main__":
    """
    Point d'entrée du programme.
    """
    compte_est_bon = CompteEstBon()
    compte_est_bon.run()