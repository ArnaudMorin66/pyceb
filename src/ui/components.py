from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QComboBox, QSpinBox

from ceb import (CebPlaque, STRPLAQUESUNIQUES, IntSearch)


class QComboboxPlq(QComboBox):
    """
    A custom QComboBox for handling CebPlaque objects.
    """
    plaque: CebPlaque

    def __init__(self, plaque, parent=None):
        """
        Initialize the QComboboxPlq.

        :param plaque: An instance of CebPlaque.
        :param parent: The parent widget, default is None.
        """
        super().__init__(parent)

        self.plaque = plaque
        self.plaque.event.connect(self.valueChanged)

        self.setDuplicatesEnabled(False)
        self.addItems(STRPLAQUESUNIQUES)
        self.setEditable(True)
        self.setCurrentText(str(plaque.value))
        self.currentTextChanged.connect(self.oncurrenttextchanged)

    def oncurrenttextchanged(self, text: str):
        """
        Slot for handling the currentTextChanged signal.

        :param text: The text of the current item.
        """
        self.plaque.event.disconnect(self.valueChanged)
        self.plaque.value = int(text) if text.isdigit() else 0
        self.plaque.event.connect(self.valueChanged)

    # noinspection PyPep8Naming
    def valueChanged(self, sender,  old_value):
        with QSignalBlocker(self):
            self.setCurrentText(str(sender.value))


class QSpinBoxSearch(QSpinBox):
    """

    """
    _search: IntSearch = None

    def __init__(self, search_value: IntSearch, parent=None):
        """
        Initialize the QSpinBoxSearch.

        :param parent: The parent widget, default is None.
        """
        super().__init__(parent)
        self.setRange(100, 999)
        self._search = search_value
        self.setValue(search_value.value)

        self.valueChanged.connect(self.onvaluechanged)
        self._search.event.connect(self.onsearchchanged)

    def onvaluechanged(self, value: int):
        """
        Slot for handling the valueChanged signal.

        :param value: The value of the spin box.
        """
        self._search.event.disconnect(self.onsearchchanged)
        self._search.value = value
        self._search.event.connect(self.onsearchchanged)

    def onsearchchanged(self, sender, old_value):
        with QSignalBlocker(self):
            self.setValue(sender.value)
