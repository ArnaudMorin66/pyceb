"""
    Calcul du compte est bon
"""
from __future__ import annotations

import asyncio
import csv
import json
import os
import pickle
import xml.etree.ElementTree as XML
from random import randint
from sys import maxsize
from typing import List

from ceb.base import CebBase
from ceb.inotify import INotify
from ceb.operation import CebOperation
from ceb.plaque import CebPlaque, LISTEPLAQUES
from ceb.status import CebStatus

class CebTirage(INotify):
    """
    Tirage Plaques et Recherche
    """

    def __init__(
            self, plaques: List[int] = (), search: int = 0, auto: bool = False
    ) -> None:
        """
            Initialise une instance de CebTirage.

            :param plaques: Liste d'entiers représentant les plaques.
            :param search: Valeur entière à rechercher.
            :param auto: Booléen indiquant si la recherche doit être automatique.
            """
        super().__init__()
        self.auto: bool = auto
        self._plaques: List[CebPlaque] = []
        self._search: int = 0
        self._solutions: List[CebBase] = []
        self._diff: int = maxsize
        self._status: CebStatus = CebStatus.Indefini
        for k in plaques:
            self._plaques.append(CebPlaque(k, self))

        self._search = search
        if search and plaques:
            self.clear()
        elif search == 0 and len(plaques) > 0:
            self._search = randint(100, 999)
            self.clear()
        else:
            self.random()

    def clear(self) -> CebStatus:
        """
        Réinitialise l'état de l'objet CebTirage.

        Cette méthode vide la liste des solutions, réinitialise la différence maximale,
        valide l'état actuel et, si l'option auto est activée, lance la résolution.

        :return: Le statut actuel de l'objet CebTirage.
        """
        self._solutions = []
        self._diff = maxsize
        self.valid()
        if self.auto:
            self.resolve()
        return self.status

    @property
    def found(self) -> list[int]:
        return sorted(set([k.value for k in self.solutions]))
    @property
    def str_found(self) -> str:
        return ", ".join(map(str, self.found))

    @property
    def search(self) -> int:
        return self._search

    @search.setter
    def search(self, value: int):
        if value == self._search:
            return
        old = self._search
        self._search = value
        self.notify(old, value)

    def random(self) -> CebStatus:
        """
        Génère un tirage aléatoire de plaques et une valeur de recherche.

        Cette méthode initialise la valeur de recherche à un nombre aléatoire entre 100 et 999,
        puis sélectionne aléatoirement 6 plaques de la liste `LISTEPLAQUES`.

        :return: Le statut actuel de l'objet CebTirage après réinitialisation.
        """
        self._search = randint(100, 999)
        liste_plaques = LISTEPLAQUES[:]
        self._plaques[:] = []
        self._plaques = \
            [CebPlaque(liste_plaques.pop(randint(0, len(liste_plaques) - 1)), self) for _ in range(6)]
        return self.clear()

    @property
    def json(self) -> str:
        return json.dumps(self.result)

    @property
    def ecart(self) -> int:
        return self._diff

    @property
    def count(self) -> int:
        return len(self.solutions)

    @property
    def solutions(self) -> List[CebBase]:
        """
            Get the list of solutions if the status is valid.

            :return: List of solutions.
            """
        return (
            self._solutions
            if self.status in [CebStatus.CompteEstBon, CebStatus.CompteApproche] else []
        )

    @property
    def status(self) -> CebStatus:
        return self._status

    @status.setter
    def status(self, value: CebStatus):
        self._status = value

    @property
    def plaques(self) -> List[CebPlaque]:
        return self._plaques

    @plaques.setter
    def plaques(self, plq: List[int]):
        for index, value in enumerate(plq[:6]):
            self._plaques[index].value = value
        self.clear()

    def valid(self) -> CebStatus:
        """
        Valide le tirage actuel.

        Cette méthode vérifie si la valeur de recherche est comprise entre 100 et 999
        et si le nombre de plaques est égal à 6. Elle vérifie également que chaque plaque
        est présente dans la liste `LISTEPLAQUES` et que leur nombre est suffisant.

        :return: Le statut actuel de l'objet CebTirage, soit `CebStatus.Valide` soit `CebStatus.Invalide`.
        """
        self._status = CebStatus.Valide if 100 <= self._search <= 999 and len(
            self._plaques) == 6 else CebStatus.Invalide
        if self._status == CebStatus.Valide:
            for plaque in self._plaques:
                if LISTEPLAQUES.count(plaque.value) < self._plaques.count(plaque):
                    self._status = CebStatus.Invalide
                    break
        return self._status

    def notify(self, param1, param2):
        self.clear()

    @property
    def solution(self) -> CebBase | None:
        return self.solutions[0] if self.count != 0 else None

    def _add_solution(self, sol: CebBase):
        """
        Ajoute l'opération sol aux solutions si la valeur est plus proche ou égale
        à celles déjà trouvées.

        :param sol: L'opération à ajouter aux solutions.
        :return: Rien.
        """
        diff: int = abs(sol.value - self._search)
        if diff > self._diff:
            return
        if diff != self._diff:
            self._solutions = [sol]
            self._diff = diff
        elif sol not in self._solutions:
            self._solutions.append(sol)

    def resolve(
            self, plaques: List[int | CebPlaque] = (), search: int = 0
    ) -> CebStatus:
        """
        Résout le problème en utilisant les plaques et la valeur de recherche fournies.

        :param plaques: Liste d'entiers ou d'objets CebPlaque représentant les plaques.
        :param search: Valeur entière à rechercher.
        :return: Le statut actuel de l'objet CebTirage.
        """
        if search and len(plaques) == 6:
            self._search = search
            self.plaques = plaques

        if not self.auto:
            self.clear()
        if self._status == CebStatus.Invalide:
            return self._status

        self._status = CebStatus.EnCours
        self.resolve_stack(self.plaques[:])
        self._solutions.sort(key=lambda sol: sol.rank)
        self.status = CebStatus.CompteEstBon \
            if self._solutions[0].value == self._search else CebStatus.CompteApproche
        return self._status

    async def resolve_async(self) -> CebStatus:
        """
        Asynchronously resolves and returns a CebStatus object.

        This method utilizes asyncio's `to_thread` to run the synchronous `resolve` method in a separate thread,
        allowing for non-blocking execution in an asynchronous environment. It is particularly useful when dealing
        with I/O-bound tasks that do not natively support asynchronous execution but can benefit from being
        executed in a separate thread.

        Returns:
            CebStatus: The result of the `resolve` method.

        """
        return await asyncio.to_thread(self.resolve)

    def resolve_stack(self, plaques: List) -> None:
        """
        resolve_stack(plaques: List) -> None
            Iterates through a list of plaques, applying a series of operations to each element and recursively processing the resulting lists until no more operations can be performed.

            Parameters:
            plaques (List): The initial list of plaques to be processed

        next_list(current_list: List, ceb_operation: CebOperation, i: int, j: int) -> List
            Generates a new list by applying a given operation to elements at specified indices and excluding those elements from the resulting list.

            Parameters:
            current_list (List): The list currently being processed
            ceb_operation (CebOperation): The operation to be applied to the elements at the specified indices
            i (int): The first index to be operated on
            j (int): The second index to be operated on

            Returns:
            List: A new list resulting from the operation and exclusion of specified elements
        """

        def next_list(current_list: List, ceb_operation: CebOperation, ii: int, jj: int) -> List:
            return [ceb_operation] + [x for k, x in enumerate(current_list) if k not in (ii, jj)]

        stack = [plaques]
        while stack:
            current_liste = stack.pop()
            for ix, plq in enumerate(current_liste):
                self._add_solution(plq)
                for jx in range(ix + 1, len(current_liste)):
                    q = current_liste[jx]
                    for operation in "x+-/":
                        oper: CebOperation = CebOperation(plq, operation, q)
                        if oper.value:
                            stack.append(next_list(current_liste, oper, ix, jx))

    @property
    def result(self) -> dict:
        return {
            "plaques": [k.value for k in self.plaques],
            "search": self.search,
            "status": cebstatus_to_str(self.status),
            "found": self.found,
            "ecart": self.ecart,
            "count": self.count,
            "solutions": [solution.operations for solution in self.solutions]
        }

    def __repr__(self):
        return self.json

    @staticmethod
    def solve(
            plaques: List[int] = (), search: int = 0, auto: bool = False
    ) -> CebTirage:
        """
        Crée une instance de CebTirage et résout le problème.

        :param plaques: Liste d'entiers représentant les plaques.
        :param search: Valeur entière à rechercher.
        :param auto: Booléen indiquant si la recherche doit être automatique.
        :return: Une instance de CebTirage après résolution.
        """
        _tirage = CebTirage(plaques, search, auto)
        _tirage.resolve()
        return _tirage

    def save_to_json(self, filename: str):
        """
        Sauvegarde les résultats du tirage dans un fichier JSON.

        Args:
            filename (str): Le nom du fichier dans lequel sauvegarder les résultats.
        """

        with open(filename, "w", encoding="utf-8") as file:
            # noinspection PyTypeChecker
            json.dump(self.result, file, ensure_ascii=False, indent=4)

    def save_to_xml(self, filename: str):
        """
        Sauvegarde les résultats du tirage dans un fichier XML.

        Args:
            filename (str): Le nom du fichier dans lequel sauvegarder les résultats.
        """
        root = XML.Element("ceb")
        plaques_element = XML.SubElement(root, "plaques")
        for plaque in self.plaques:
            XML.SubElement(plaques_element, "plaque").text = str(plaque)
        XML.SubElement(root, "search").text = str(self.search)
        XML.SubElement(root, "status").text = cebstatus_to_str(self.status)
        XML.SubElement(root, "found").text = str(self.found)
        XML.SubElement(root, "ecart").text = str(self.ecart)
        XML.SubElement(root, "count").text = str(self.count)

        solutions_element = XML.SubElement(root, "solutions")
        for solution in self.solutions:
            solution_element = XML.SubElement(solutions_element, "solution")
            for operation in solution.operations:
                XML.SubElement(solution_element, "operation").text = operation

        tree = XML.ElementTree(root)
        tree.write(filename, encoding="utf-8", xml_declaration=True)

    def save_to_pickle(self, filename: str):
        with open(filename, "wb") as file:
            # noinspection PyTypeChecker
            pickle.dump(self.result, file)

    def save_to_csv(self, filename: str):
        """
        Sauvegarde les résultats du tirage dans un fichier CSV.

        Args:
            filename (str): Le nom du fichier dans lequel sauvegarder les résultats.
        """
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Plaques", "Search", "Status", "Found", "Ecart", "Count", "Solutions"])
            writer.writerow([
                ",".join(map(str, [k.value for k in self.plaques])),
                self.search,
                cebstatus_to_str(self.status),
                ",".join(map(str, self.found)),
                self.ecart,
                self.count,
                ";".join([" ".join(sol.operations) for sol in self.solutions])
            ])

    def save(self, filename: str):
        """
        Sauvegarde les résultats du tirage dans un fichier.

        Args:
            filename (str): Le nom du fichier dans lequel sauvegarder les résultats..
        """
        _, extension = os.path.splitext(filename)
        save_methods = {
            ".json": self.save_to_json,
            ".xml": self.save_to_xml,
            ".pkl": self.save_to_pickle,
            ".csv": self.save_to_csv
        }
        method = save_methods.get(extension, self.save_to_json)
        # noinspection PyArgumentList
        method(filename)


def cebstatus_to_str(status: CebStatus) -> str:
    """
    Convertit un objet CebStatus en chaîne de caractères.

    Args:
        status (CebStatus): L'objet CebStatus à convertir.

    Returns:
        str: La chaîne de caractères représentant l'objet CebStatus.
    """
    return {
        CebStatus.EnCours: "⚙️ En cours",
        CebStatus.CompteEstBon: "😀 Compte est bon",
        CebStatus.CompteApproche: "🙄 Compte approché",
        CebStatus.Invalide: " ❌ Invalide"
    }.get(status, "Inconnu")


def resolve(plaques: List[int] = (), search: int = 0, auto: bool = False) -> CebTirage:
    """
    Résout le problème en créant une instance de CebTirage et en appelant sa méthode solve.

    :param plaques: Liste d'entiers représentant les plaques.
    :param search: Valeur entière à rechercher.
    :param auto: Booléen indiquant si la recherche doit être automatique.
    :return: Une instance de CebTirage après résolution.
    """
    return CebTirage.solve(plaques, search, auto)


if __name__ == "__main__":
    """
    Point d'entrée principal du script.

    Cette section du code est exécutée lorsque le script est exécuté directement.
    Elle crée une instance de `CebTirage`, résout le problème et affiche les résultats.
    """
    print("")
    t = CebTirage(auto=False)
    t.resolve()
    print(f"search: {t.search}")
    print("plaques : ")
    for p in t.plaques:
        print(f"\t{p.value}")
    print("")
    match t.status:
        case CebStatus.CompteEstBon:
            print("Le Compte est bon")
        case CebStatus.CompteApproche:
            print(f"Compte approché: {t.found}")
        case CebStatus.Valide:
            print("Non calculé")
            exit(1)
        case _:
            print("Tirage invalide")
    print("")
    print(f"{t.count} solutions")
    for i, s in enumerate(t.solutions):
        print(f"\t{i}: \t{s}")
