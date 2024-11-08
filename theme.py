from enum import Enum

from PySide6.QtWidgets import QWidget


class Theme(Enum):
    """
    Enumération représentant les thèmes disponibles.
    """
    light = 0
    dark = 1

class ThemeManager:
    """
    Classe pour gérer les thèmes de l'application.
    """
    _theme: Theme = Theme.dark
    _window: QWidget = None

    def __init__(self, window, theme: Theme = Theme.dark):
        """
        Initialise le gestionnaire de thème avec le thème et la fenêtre spécifiés.

        :param theme: Le thème à utiliser (light ou dark).
        :param window: La fenêtre QWidget à laquelle appliquer le thème.
        """
        self._theme = theme
        self._window = window

    @property
    def value(self):
        """
        Retourne le thème actuel.

        :return: Le thème actuel.
        """
        return self._theme

    @value.setter
    def value(self, theme: Theme):
        """
        Définit le thème et applique les changements de style.

        :param theme: Le nouveau thème à appliquer.
        """
        self._theme = theme
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
        self.value = Theme.light if self.value == Theme.dark else Theme.dark

    def init_theme(self):
        """
        Applique le style du thème actuel à la fenêtre.
        """
        self.window.setStyleSheet("""
                    QWidget {
                        background-color: white;
                        color: black;
                    }
                    QPushButton {
                        background-color: lightgray;
                        color: black;
                    }
                """ if self.value == Theme.light else """
                   QWidget {
                       background-color: #212121;
                       color: white;
                   }
                   QPushButton {
                       background-color: #5a5a5a;
                       color: white;
                   }
               """)


