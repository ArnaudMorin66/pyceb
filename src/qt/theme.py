import glob
import os
from enum import Enum

from PySide6.QtWidgets import QWidget, QApplication


class Theme(Enum):
    """
    Enumération représentant les thèmes disponibles.
    """
    light = 0
    dark = 1

current_theme = Theme.dark
class ThemeManager:
    """
    Classe pour gérer les thèmes de l'application.
    """
    _window: QWidget = None

    def __init__(self, window, theme: Theme = Theme.dark):
        """
        Initialise le gestionnaire de thème avec le thème et la fenêtre spécifiés.

        :param window: La fenêtre QWidget à laquelle appliquer le thème.
        """
        self._window = window
        self.theme = theme

    @property
    def theme(self):
        global current_theme
        """
        Retourne le thème actuel.

        :return: Le thème actuel.
        """
        return current_theme

    @theme.setter
    def theme(self, theme: Theme):
        """
        Définit le thème actuel.

        :param theme: Le thème à définir.
        """
        self.set_theme(theme)

    def set_theme(self, theme: Theme):
        """
        Définit le thème actuel.

        :param theme: Le thème à définir.
        """
        global current_theme
        current_theme = theme
        self.init_theme()


    @property
    def window(self):
        """
        Retourne la fenêtre actuelle.

        :return: La fenêtre QWidget actuelle.
        """
        return self._window


    def switch_theme(self):
        """
        Bascule entre les thèmes clair et sombre.
        """
        global current_theme
        current_theme = Theme.light if self.theme == Theme.dark else Theme.dark
        self.init_theme()


    def init_theme(self):
        """
        Applique le style du thème actuel à la fenêtre.
        """
        global current_theme
        nom = "light" if self.theme == Theme.light else "dark"
        filename = f"{os.path.dirname(__file__)}{os.sep}theme{os.sep}{nom}style.qss"
        with open(filename, "r") as f:
            QApplication.instance().setStyleSheet(f.read())