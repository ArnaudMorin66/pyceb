from typing import override

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QComboBox, QSpinBox

from ceb import (CebPlaque, STRPLAQUESUNIQUES, CebTirage, CebSearch)
from utils import IObserverNotify


class QComboboxPlq(QComboBox, IObserverNotify):
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
        self.plaque.connect(self)

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
        self.plaque.disconnect(self)
        self.plaque.value = int(text) if text.isdigit() else 0
        self.plaque.connect(self)

    @override
    def observer_notify(self, plaque: CebPlaque, old: int):
        """
        Slot for handling the notify signal.

        :param plaque: The CebPlaque object.
        :param old: The old value of the plaque.
        """
        with QSignalBlocker(self):
            self.setCurrentText(str(plaque.value))


class QSpinBoxSearch(QSpinBox, IObserverNotify):
    """

    """
    _tirage: CebTirage = None

    def __init__(self, tirage, parent=None):
        """
        Initialize the QSpinBoxSearch.

        :param parent: The parent widget, default is None.
        """
        super().__init__(parent)
        self.setRange(100, 999)
        self._tirage = tirage
        self.setValue(tirage.search)

        self.valueChanged.connect(self.onvaluechanged)
        self._tirage.cebsearch.connect(self)

    def onvaluechanged(self, value: int):
        """
        Slot for handling the valueChanged signal.

        :param value: The value of the spin box.
        """
        self._tirage.cebsearch.disconnect(self)
        self._tirage.search = value
        self._tirage.cebsearch.connect(self)

    @override
    def observer_notify(self, sender: CebSearch, old):
        """
        Notification handler for updating the spin box value from the sender.

        :param sender: The object sending the notification.
        :param old: The old value before the update.
        """
        with QSignalBlocker(self):
            self.setValue(sender.value)
