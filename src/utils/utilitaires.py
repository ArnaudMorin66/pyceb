import argparse
import time
from argparse import Namespace, ArgumentParser, BooleanOptionalAction
from functools import wraps
from typing import Callable



def singleton(class_):
    """
    Decorator to make a class a singleton. Ensures that only one instance of the class exists.

    :param class_: The class to be turned into a singleton.
    :type class_: type
    :return: The singleton instance of the class.
    :rtype: type
    """
    instances = {}

    def get_instance(*args, **kwargs):
        """
        Retourne l'instance unique de la classe.

        :param args: Arguments positionnels pour l'initialisation de la classe.
        :param kwargs: Arguments nommés pour l'initialisation de la classe.
        :return: L'instance unique de la classe.
        """
        if class_ not in instances:
            kl = class_(*args, **kwargs)
            instances[class_] = kl
        return instances[class_]

    return get_instance


# noinspection PyUnresolvedReferences,PyIncorrectDocstring
def parse_args() -> Namespace:
    """
    Parses command-line arguments and returns a Namespace object.

    This function sets up the argument parser with various options related to 'Compte est bon',
    such as UI toggle, plaques (numbers to be used), target value to search for, JSON display,
    wait for return, and an option to save the draw.

    See Also
    --------
    argparse.Namespace : Object to hold attributes parsed from command line

    Raises
    ------
    SystemExit
        If the arguments are invalid or help/version information is requested

    Returns
    -------
    Namespace
        A Namespace object populated with the parsed arguments

    Parameters
    ----------
    -q, --qt
        bool : Toggles UI
    -p, --plaques
        List[int] : Plaques (numbers to be used)
    -s, --search
        int : Target value to search for
    -j, --json
        bool : Toggles JSON display of the draw
    -w, --wait
        bool : Waits for a return value
    integers
        List[int] : Plaques and the value to search for
    -S, --save
        argparse.FileType("r") : File to save the draw
    """
    parser = ArgumentParser(description="Compte est bon")
    parser.add_argument("-q", "--qt", type=bool, action=BooleanOptionalAction, help="ui", default=False)
    parser.add_argument("-p", "--plaques", nargs="+", type=int, help="plaques", default=[])
    parser.add_argument("-s", "--search", type=int, help="Valeur à chercher", default=0)
    parser.add_argument("-j", "--json", type=bool, action=BooleanOptionalAction, help="affichage du tirage",
                        default=False)
    parser.add_argument("-w", "--wait", type=bool, action=BooleanOptionalAction, help="attendre retour",
                        default=False)
    parser.add_argument("integers", metavar="N", type=int, nargs="*", help="plaques & valeur à chercher")
    parser.add_argument("-S", "--save", type=argparse.FileType("r"), help="Sauvegarde du tirage",
                        default=None)
    return parser.parse_args()


def ellapsed_exec(func: Callable) -> Callable:
    """
    Decorator function to measure the elapsed execution time of the given function in nanoseconds.

    Args:
        func (Callable): The function to be decorated.

    Returns:
        Callable: A wrapper function which executes the original function and returns a tuple containing the elapsed time
        in nanoseconds and the result of the function call.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.process_time_ns()
        result = func(*args, **kwargs)
        return time.process_time_ns() - start_time, result

    return wrapper


class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class SignalBase:
    """
    Classe de base pour la gestion des signaux et des observateurs.
    """

    def __init__(self):
        """
        Initialise une nouvelle instance de SignalBase.
        """
        self._observers = []
        self._enabled = True

    def connect(self, observer):
        """
        Connecte un observateur au signal.

        :param observer: La fonction observatrice à connecter.
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def disconnect(self, observer):
        """
        Déconnecte un observateur du signal.

        :param observer: La fonction observatrice à déconnecter.
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def disconnect_all(self):
        """
        Déconnecte tous les observateurs du signal.
        """
        self._observers.clear()

    def is_enabled(self):
        """
        Vérifie si le signal est activé.

        :return: True si le signal est activé, sinon False.
        """
        return self._enabled

    def enable(self):
        """
        Active le signal.
        """
        self._enabled = True

    def disable(self):
        """
        Désactive le signal.
        """
        self._enabled = False

    def is_connect(self, observer):
        """
        Vérifie si un observateur est connecté au signal.

        :param observer: La fonction observatrice à vérifier.
        :return: True si l'observateur est connecté, sinon False.
        """
        return observer in self._observers

    def has_connect(self):
        """
        Vérifie s'il y a des observateurs connectés au signal.

        :return: True s'il y a des observateurs connectés, sinon False.
        """
        return len(self._observers) > 0

    def emit(self, *args, **kwargs):
        """
        Émet le signal à tous les observateurs connectés.

        :param args: Arguments positionnels à passer aux observateurs.
        :param kwargs: Arguments nommés à passer aux observateurs.
        """
        if self._enabled:
            for observer in self._observers:
                observer(*args, **kwargs)


class SignalObject[T](SignalBase):
    """
    Classe SignalObject qui hérite de SignalBase et gère une valeur de type g��nérique T.
    Émet un signal lorsque la valeur change.
    """
    _value: T

    def __init__(self, value: T | None = None):
        """
        Initialise une nouvelle instance de SignalObject.

        :param value: La valeur initiale de l'objet, de type T ou None.
        """
        super().__init__()
        if value is not None:
            self._value = value

    @property
    def value(self):
        """
        Obtient la valeur actuelle de l'objet.

        :return: La valeur actuelle de l'objet.
        """
        return self._value

    @value.setter
    def value(self, new_value: T):
        """
        Définit une nouvelle valeur pour l'objet et émet un signal si la valeur change.

        :param new_value: La nouvelle valeur à définir.
        """
        if self._value == new_value:
            return
        old_value = self._value
        self._value = new_value
        self.emit(new_value, old_value)

    def __repr__(self):
        """
        Retourne une représentation sous forme de chaîne de la valeur de l'objet.

        :return: La valeur de l'objet sous forme de chaîne.
        """
        return str(self._value)
