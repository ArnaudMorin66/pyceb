from enum import Enum

from PySide6.QtWidgets import QWidget


class Theme(Enum):
    light = 0
    dark = 1

class ThemeManager:
    _theme: Theme = Theme.dark
    _window: QWidget = None
    def __init__(self, theme: Theme, window):
        self._theme = theme
        self._window = window

    @property
    def value(self):
        return self._theme

    @value.setter
    def value(self, theme: Theme):
        self._theme = theme
        self.init_theme()

    @property
    def window(self):
        return self._window

    def switch_theme(self):
        if self.value == Theme.dark:
            self.value = Theme.light
        else:
            self.value = Theme.dark

    def init_theme(self):
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


