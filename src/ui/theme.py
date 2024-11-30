import os
from enum import Enum

from PySide6.QtWidgets import QApplication

from utils.utilitaires import singleton

THEME_DIRECTORY = os.path.join(os.path.dirname(__file__), "theme")


class Theme(Enum):
    """
    Enumération représentant les thèmes disponibles.
    """
    light = 0
    dark = 1


@singleton
class QThemeManager:
    """
    Classe pour gérer les thèmes de l'application.
    """
    _theme: Theme = Theme.dark

    def __init__(self, theme: Theme = Theme.dark):
        """
        Initialise une nouvelle instance de ThemeManager.

        :param theme: Le thème à utiliser pour l'initialisation.
        """
        self._theme = theme
        load_theme(theme)

    @property
    def theme(self):
        """
        Retourne le thème actuel.
        :return: Le thème actuel.
        """
        return self._theme

    @theme.setter
    def theme(self, theme: Theme):
        """
        Définit le thème actuel.

        :param theme: Le thème à définir.
        """
        if self._theme == theme:
            return
        self._theme = theme
        load_theme(theme)

    def switch_theme(self):
        """
        Bascule entre les thèmes clair et sombre.
        """
        self.theme = Theme.light if self.theme == Theme.dark else Theme.dark


def load_theme(theme: Theme):
    """
    Applique le style du thème actuel à la fenêtre.
    """
    theme_name = "light" if theme == Theme.light else "dark"
    style_file_path = os.path.join(os.path.dirname(__file__), "theme", f"{theme_name}.qss")
    with open(style_file_path, "r") as f:
        # noinspection PyUnresolvedReferences
        QApplication.instance().setStyleSheet(f.read())




