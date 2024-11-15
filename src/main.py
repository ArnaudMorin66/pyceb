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
from rich.console import Console
from rich.table import Table

from ceb import CebTirage, CebStatus
from qt.qtceb import QtCeb
def exec_time(fun: Callable, *vals: object) -> tuple[int, any]:
    """
    Mesure le temps d'exécution d'une fonction.

    Args:
        fun (Callable): La fonction à exécuter.
        *vals (object): Les arguments de la fonction.

    Returns
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
        usage: main.py [-h] [-q | --qt | --no-qt] [-p PLAQUES [PLAQUES ...]] [-s SEARCH] [-j | --json | --no-json] [-w | --wait | --no-wait] [-S | --save | --no-save] [N ...]

        """
        self.args = None
        self.parser = None
        self.console = Console()
        self.wait = False
        self.parse_args()
        self.tirage = CebTirage()

    def parse_args(self):
        """Analyse les arguments de la ligne de commande."""
        self.parser = ArgumentParser(description="Compte est bon")
        self.parser.add_argument("-q", "--qt", type=bool, action=BooleanOptionalAction, help="qt", default=False)
        self.parser.add_argument("-p", "--plaques", nargs="+", type=int, help="plaques", default=[])
        self.parser.add_argument("-s", "--search", type=int, help="Valeur à chercher", default=0)
        self.parser.add_argument("-j", "--json", type=bool, action=BooleanOptionalAction, help="affichage du tirage",
                                 default=False)
        self.parser.add_argument("-w", "--wait", type=bool, action=BooleanOptionalAction, help="attendre retour",
                                 default=False)
        self.parser.add_argument("integers", metavar="N", type=int, nargs="*", help="plaques & valeur à chercher")
        self.parser.add_argument("-S", "--save", type=bool, action=BooleanOptionalAction, help="Sauvegarde du tirage",
                                 default=None)
        self.args = self.parser.parse_args()
        if self.args.qt:
            QtCeb.run()
            sys.exit(0)

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
        if self.args.json:
            self.tirage.resolve()
            self.console.print(self.tirage.json, style="bold green")
        else:
            self.console.print("#### Tirage du compte est bon ####", style="bold blue")
            self.console.print(f"Tirage: {', '.join(map(str, self.tirage.plaques))}\tRecherche: {self.tirage.search}",
                               style="bold yellow")

            ellapsed, status = exec_time(self.tirage.resolve)
            self.console.print()

            match status:
                case CebStatus.CompteEstBon:
                    self.console.print("Le Compte est bon", style="bold green")
                case CebStatus.CompteApproche:
                    self.console.print(f"Compte approché: {self.tirage.found}", style="bold yellow")
                case _:
                    self.console.print("Tirage invalide", style="bold red")
            color = "green" if self.tirage.status == CebStatus.CompteEstBon else "yellow"
            self.console.print(f"Nombre de solutions trouvées: {self.tirage.count}", style=f"bold {color}")
            self.console.print(f"Durée du calcul: {ellapsed / 1.E+09: 0.3f} s", style=f"bold {color}")
            if self.tirage.count > 0:
                table = Table(title="Solutions")
                for col in ["Index", "Opération 1", "Opération 2", "Opération 3", "Opération 4", "Opération 5"]:
                    table.add_column(col, style=color, no_wrap=True)

                for i, s in enumerate(self.tirage.solutions):
                    table.add_row(str(i + 1), s.op1, s.op2, s.op3, s.op4, s.op5)

                self.console.print(table)
            self.console.print()

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
            match self.args.save:
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
