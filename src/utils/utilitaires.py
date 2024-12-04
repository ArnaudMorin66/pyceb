import argparse
import time
from argparse import Namespace, ArgumentParser, BooleanOptionalAction
from functools import wraps
from typing import Callable


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


