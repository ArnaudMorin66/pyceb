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
from typing import List, overload

from ceb.base import CebBase
from ceb.notify import IPlaqueNotify
from ceb.operation import CebOperation
from ceb.plaque import CebPlaque, LISTEPLAQUES
from ceb.status import CebStatus
from utils import ObservableObject

EXTENSION_METHODS = {
    ".json": "save_to_json",
    ".xml": "save_to_xml",
    ".pkl": "save_to_pickle",
    ".csv": "save_to_csv"
}

OPERATIONS = ["x", "+", "-", "/"]

class CebTirage(IPlaqueNotify):
    """
    Tirage Plaques et Recherche
    """

    def __init__(
            self, plaques=None, search: int = 0) -> None:
        """
            Initialise une instance de CebTirage.

            :param plaques: Liste d'entiers représentant les plaques.
            :param search: Valeur entière à rechercher.
            """
        super().__init__()
        if plaques is None:
            plaques = []
        self._plaques: List[CebPlaque] = []

        self._search: ObservableObject[int] = ObservableObject(0)
        self._solutions: List[CebBase] = []
        self._diff: int = maxsize
        self._status: CebStatus = CebStatus.Indefini

        for _ in range(6):
            self._plaques.append(CebPlaque(0, self))

        self._search.value = search

        if search and plaques:
            pass
        elif search == 0 and len(plaques) > 0:
            self._search.value = randint(100, 999)
        else:
            self.random()
        self.clear()

    def connect_search(self, observer):
        """
        Attache un observateur à l'objet de recherche.

        :param observer: L'observateur à attacher.
        """
        self._search.connect(observer)

    def disconnect_search(self, observer):
        """
        Détache un observateur de l'objet de recherche.

        :param observer: L'observateur à détacher.
        """
        self._search.disconnect(observer)

    def connect_plaques(self, plaque_notify: IPlaqueNotify=None):
        """
        Attache un observateur à toutes les plaques.

        :param plaque_notify: L'observateur à attacher.
        """
        for plaque in self._plaques:
            plaque.connect(plaque_notify if plaque_notify else self)

    def disconnect_plaques(self, notify_plaque: IPlaqueNotify=None):
        """
        Détache un observateur de toutes les plaques.

        :param notify_plaque: L'observateur à détacher.
        """
        for plaque in self._plaques:
            plaque.disconnect(notify_plaque if notify_plaque else self)

    def block_plaques(self, value: bool = True):
        """
        Bloque les notifications pour toutes les plaques.

        :param value: True pour bloquer les notifications, False pour les débloquer.
        """
        for plaque in self._plaques:
            plaque.disable(value)


    def clear(self) -> CebStatus:
        """
        Réinitialise l'état de l'objet CebTirage.

        Cette méthode vide la liste des solutions, réinitialise la différence maximale,
        valide l'état actuel.

        :return: Le statut actuel de l'objet CebTirage.
        """
        self._solutions = []
        self._diff = maxsize
        self.valid()
        return self.status

    @property
    def found(self) -> list[int]:
        """
        Get unique, sorted list of values from solutions

        Returns:
            list[int]: A unique, sorted list of integer values from self.solutions.
        """
        return sorted(set([k.value for k in self.solutions]))

    @property
    def str_found(self) -> str:
        """
        str_found

        Returns a comma-separated string of found elements.

        Returns:
             str: A string containing the elements of the 'found' list, separated by commas.
        """
        return ", ".join(map(str, self.found))

    @property
    def search(self) -> int:
        """
        Represents a search property.

        This property returns the value of the `_search` attribute's `value`.

        @property
        @return: The integer value of the `_search` attribute.
        """
        return self._search.value

    @search.setter
    def search(self, value: int):
        """
        Set the search value and clear the results if the value changes.

        Setter for the search attribute, which updates the value and clears any
        existing results if the new value differs from the current one.

        Args:
            value (int): The new search value.

        Raises:
            None

        Returns:
            None
        """
        if value == self._search.value:
            return
        self._search.value = value
        self.clear()

    def random(self) -> CebStatus:
        """
        Génère un tirage aléatoire de plaques et une valeur de recherche.

        Cette méthode initialise la valeur de recherche à un nombre aléatoire entre 100 et 999,
        puis sélectionne aléatoirement 6 plaques de la liste `LISTEPLAQUES`.

        :return: Le statut actuel de l'objet CebTirage après réinitialisation.
        """
        self.disconnect_plaques()
        self.search = randint(100, 999)
        liste_plaques = LISTEPLAQUES[:]
        for plaque in self._plaques:
            index = randint(0, len(liste_plaques) - 1)
            plaque.value = liste_plaques[index]
            liste_plaques.pop(index)
        self.connect_plaques()
        return self.clear()

    @property
    def json(self) -> str:
        """

        Returns the result of the object in JSON format.

        @return: JSON string representation of the result attribute.
        @rtype: str
        """
        return json.dumps(self.result)

    @property
    def ecart(self) -> int:
        """
        Calculate the difference between two values.

        Returns:
            int: The difference between the compared values.
        """
        return self._diff

    @property
    def count(self) -> int:
        """
        Returns the number of solutions.

        This property calculates the number of elements in the 'solutions' list and returns it. It provides a way to access the number of stored solutions without directly interacting with the 'solutions' list.

        Returns:
            int: The number of solutions in the list.
        """
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
        """
        Get the current status of the object.

        This property retrieves the current status of the object, which is an instance of CebStatus.

        Returns:
            CebStatus: The current status of the object.
        """
        return self._status

    @status.setter
    def status(self, value: CebStatus):
        """
        Sets the status of the object to the given value.

        Parameters:
            value (CebStatus): The new status to be set.

        """
        self._status = value

    @property
    def plaques(self) -> List[CebPlaque]:
        """
        Returns a list of CebPlaque objects associated with this instance.

        Returns
        -------
        List[CebPlaque]
            A list containing CebPlaque objects.
        """
        return self._plaques

    @plaques.setter
    def plaques(self, plq: List[int]):
        """
        Sets the values of the plaques attribute with the provided list of integers.
        Only the first six values of the provided list are considered.

        Args:
            plq (List[int]): A list of integers representing the new values for the
            plaques attribute.
        """
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
        self._status = CebStatus.Valide if 100 <= self._search.value <= 999 and len(
            self._plaques) == 6 else CebStatus.Invalide
        if self._status == CebStatus.Valide:
            for plaque in self._plaques:
                if LISTEPLAQUES.count(plaque.value) < self._plaques.count(plaque):
                    self._status = CebStatus.Invalide
                    break
        return self._status

    def plaque_notify(self, sender, old):
        """
        Notifie un changement de paramètre et réinitialise l'état de l'objet CebTirage.

        Cette méthode appelle la méthode `clear` pour réinitialiser l'état de l'objet.

        :param sender: Ancienne valeur du paramètre.
        :param old: Nouvelle valeur du paramètre.
        """
        self.clear()

    @property
    def solution(self) -> CebBase | None:
        """
        Retourne la première solution trouvée si elle existe.

        :return: La première solution trouvée ou None si aucune solution n'est disponible.
        """
        return self.solutions[0] if self.count != 0 else None

    def _add_solution(self, sol: CebBase):
        """
        Ajoute l'opération sol aux solutions si la valeur est plus proche ou égale
        à celles déjà trouvées.

        :param sol: L'opération à ajouter aux solutions.
        :return: Rien.
        """
        diff: int = abs(sol.value - self._search.value)
        if diff > self._diff:
            return
        if diff != self._diff:
            self._solutions = [sol]
            self._diff = diff
        elif sol not in self._solutions:
            self._solutions.append(sol)

    def solve(self):
        """
        Résout le problème en utilisant les plaques et la valeur de recherche fournies.

        :return: Le statut actuel de l'objet CebTirage.
        """
        if self._status == CebStatus.Invalide:
            return self._status

        self._status = CebStatus.EnCours
        self.solve_stack(self.plaques[:])
        self._solutions.sort(key=lambda sol: sol.rank)
        self.status = CebStatus.CompteEstBon \
            if self._solutions[0].value == self.search else CebStatus.CompteApproche
        return self._status

    def solve_with_param(
            self, plaques: List[int | CebPlaque] , search: int ) -> CebStatus:
        """
        Résout le problème en utilisant les plaques et la valeur de recherche fournies.

        :param plaques: Liste d'entiers ou d'objets CebPlaque représentant les plaques.
        :param search: Valeur entière à rechercher.
        :return: Le statut actuel de l'objet CebTirage.
        """
        self._search.value = search
        self.plaques = plaques
        return self.solve()


    async def solve_async(self) -> CebStatus:
        """
        Résout le problème de manière asynchrone.

        Cette méthode utilise `asyncio.to_thread` pour exécuter la méthode solve` dans un thread séparé.

        :return: Le statut actuel de l'objet CebTirage après résolution.
        """
        return await asyncio.to_thread(self.solve)

    def solve_stack(self, plaques: List[CebBase]) -> None:
        """
        Résout le problème en utilisant une pile pour explorer toutes les combinaisons possibles de plaques et d'opérations.

        :param plaques: Liste de plaques à utiliser pour la résolution.
        """

        def next_list(current_list: List[CebBase], ceb_operation: CebOperation, ii: int, jj: int) -> List[CebBase]:
            """
            Génère une nouvelle liste en appliquant une opération sur deux plaques et en excluant les plaques utilisées.

            :param current_list: Liste actuelle de plaques.
            :param ceb_operation: Opération à appliquer.
            :param ii: Index de la première plaque.
            :param jj: Index de la deuxième plaque.
            :return: Nouvelle liste de plaques après application de l'opération.
            """
            return [x for k, x in enumerate(current_list) if k not in (ii, jj)] + [ceb_operation]

        stack = [plaques]

        while stack:
            current_liste = stack.pop()
            for ix, plq in enumerate(current_liste):
                self._add_solution(plq)
                for jx in range(ix + 1, len(current_liste)):
                    q = current_liste[jx]
                    for operation in OPERATIONS:
                        oper: CebOperation = CebOperation(plq, operation, q)
                        if oper.value:
                            stack.append(next_list(current_liste, oper, ix, jx))

    @property
    def result(self) -> dict:
        """
        Retourne un dictionnaire contenant les résultats du tirage.

        :return: Un dictionnaire avec les clés suivantes:
            - plaques: Liste des valeurs des plaques.
            - search: Valeur de recherche.
            - status: Statut actuel sous forme de chaîne de caractères.
            - found: Liste des valeurs trouvées.
            - ecart: Différence entre la valeur recherchée et la solution la plus proche.
            - count: Nombre de solutions trouvées.
            - solutions: Liste des opérations pour chaque solution.
        """
        return {
            "plaques": [k.value for k in self.plaques],
            "search": self.search,
            "status": str(self.status),
            "found": self.found,
            "ecart": self.ecart,
            "count": self.count,
            "solutions": [solution.operations for solution in self.solutions]
        }

    def __repr__(self):
        """
        Retourne une représentation JSON de l'objet CebTirage.

        :return: Une chaîne JSON représentant l'objet CebTirage.
        """
        return self.json

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
        XML.SubElement(root, "status").text = str(self.status)
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
        """
        Sauvegarde les résultats du tirage dans un fichier pickle.

        Args:
            filename (str): Le nom du fichier dans lequel sauvegarder les résultats.
        """
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
                str(self.status),
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
        method = self.get_save_method(filename)
        # noinspection PyArgumentList
        method(filename)

    def get_save_method(self, filename: str):
        """
        Retourne la méthode de sauvegarde appropriée en fonction de l'extension du fichier.
        Args:
            filename (str): Le nom du fichier.
        Returns:
            method: La méthode de sauvegarde.
        """
        _, extension = os.path.splitext(filename)
        method_name = EXTENSION_METHODS.get(extension, "save_to_json")
        return getattr(self, method_name)


def solve(
        plaques: List[int] = (), search: int = 0) -> CebTirage:
    """
    Crée une instance de CebTirage et résout le problème.

    :param plaques: Liste d'entiers représentant les plaques.
    :param search: Valeur entière à rechercher.
    :return: Une instance de CebTirage après résolution.
    """
    _tirage = CebTirage(plaques, search)
    _tirage.solve()
    return _tirage


if __name__ == "__main__":
    """
    Point d'entrée principal du script.

    Cette section du code est exécutée lorsque le script est exécuté directement.
    Elle crée une instance de `CebTirage`, résout le problème et affiche les résultats.
    """
    t = CebTirage()
    t.solve()
    print(f"search: {t.search}")
    print("plaques : ")
    for p in t.plaques:
        print(f"\t{p.value}")

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

    print(f"{t.count} solutions")
    for i, s in enumerate(t.solutions):
        print(f"\t{i}: \t{s}")
