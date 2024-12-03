from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QComboBox, QSpinBox

from ceb import (CebPlaque, STRPLAQUESUNIQUES, CebSearch)


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
        self.plaque.connect(self.observer_notify)

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
        self.plaque.disconnect(self.observer_notify)
        self.plaque.value = int(text) if text.isdigit() else 0
        self.plaque.connect(self.observer_notify)


    def observer_notify(self, plaque: CebPlaque, old: int):
        """
        Slot for handling the notify signal.

        :param plaque: The CebPlaque object.
        :param old: The old value of the plaque.
        """
        with QSignalBlocker(self):
            self.setCurrentText(str(plaque.value))


class QSpinBoxSearch(QSpinBox):
    """

    """
    _search: CebSearch = None

    def __init__(self, search, parent=None):
        """
        Initialize the QSpinBoxSearch.

        :param parent: The parent widget, default is None.
        """
        super().__init__(parent)
        self.setRange(100, 999)
        self._search = search
        self.setValue(search.value)

        self.valueChanged.connect(self.onvaluechanged)
        self._search.connect(self.search_changed)

    def onvaluechanged(self, value: int):
        """
        Slot for handling the valueChanged signal.

        :param value: The value of the spin box.
        """
        self._search.disconnect(self.search_changed)
        self._search.value = value
        self._search.connect(self.search_changed)

    def search_changed(self, new_value, old_value):

        with QSignalBlocker(self):
            self.setValue(new_value)
