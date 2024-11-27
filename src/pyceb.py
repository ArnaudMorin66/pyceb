# .\venv\Scripts\python.exe
"""
Tirage du Compte est bon
"""

import sys
from argparse import Namespace

import keyboard
from rich.console import Console
from rich.table import Table

from ceb.status import CebStatus
from ceb.tirage import CebTirage
# from ceb import CebTirage, CebStatus
from ui.qceb import qceb_exec
from util.utilitaires import parse_args, ellapsed_exec


class QCompteEstBon:
    """
    Classe principale pour le jeu du Compte est bon.
    """
    args: Namespace = None

    def __init__(self, arguments: Namespace):
        """
        Initializes the MainApplication with provided arguments and sets up the console, wait flag,
        and tirage object.

        Args:
            arguments (Namespace): The command-line arguments provided to the application.
        """
        self.args = arguments
        self.console = Console()
        self.wait = False
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


    @ellapsed_exec
    def run_tirage(self):
        """
        Decorator that measures the elapsed execution time of a function.

        Parameters
        ----------
        self: Any
            The instance of the class on which the decorated method is called.

        Returns
        -------
        Any
            Returns the result of the method it decorates.
        """
        return self.tirage()

    def display_tirage(self):
        """
        Affiche le tirage et les résultats du calcul.
        """
        if self.args.json:
            self.tirage.solve()
            self.console.print(self.tirage.json, style="bold green")
        else:
            self.console.print("#### Tirage du compte est bon ####", style="bold blue")
            self.console.print(f"Tirage: {', '.join(map(str, self.tirage.plaques))}\tRecherche: {self.tirage.search}",
                               style="bold yellow")

            ellapsed, status =  self.run_tirage()

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

    def save_file(self):
        if self.args.save is None:
            return
        self.tirage.save(self.args.save)

    def run(self):
        """
        Exécute le programme principal.
        """
        self.configure_tirage()
        self.display_tirage()
        self.save_file()
        print("<FINI>")
        if self.args.wait:
            print("(q) pour finir", end="\n")
            keyboard.wait("q")
        else:
            print("\n")
        return 0


if __name__ == "__main__":
    # Analyse les arguments de la ligne de commande
    args: Namespace = parse_args()

    # Vérifie si l'option Qt est activée
    if args.qt:
        # Exécute l'interface Qt
        qceb_exec()
    else:
        # Crée une instance de CompteEstBon et exécute le programme principal
        compte_est_bon = QCompteEstBon(args)
        compte_est_bon.run()
