from PySide6.QtWidgets import QComboBox, QSpinBox

from ceb import (IPlaqueNotify, ITypeNotify,
                 CebPlaque, STRPLAQUESUNIQUES, CebTirage)


class QComboboxPlq(QComboBox, IPlaqueNotify):
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
        self.plaque.value = int(text) if text.isdigit() else 0

    def plaque_notify(self, plaque: CebPlaque, old: int):
        """
        Slot for handling the notify signal.

        :param plaque: The CebPlaque object.
        :param old: The old value of the plaque.
        """
        self.currentTextChanged.disconnect(self.oncurrenttextchanged)
        self.setCurrentText(str(plaque.value))
        self.currentTextChanged.connect(self.oncurrenttextchanged)


class QSpinBoxSearch(QSpinBox, ITypeNotify[int]):
    """
    QSpinBoxSearch is a spin box widget for handling search values in the application.

    This class inherits from QSpinBox and ITypeNotify[int], and is used to manage integer search values.
    It initializes with a given tirage object, sets up the spin box range and properties, and connects
    signals to slots for handling value changes.

    Attributes:
        _tirage (CebTirage): The tirage object associated with this spin box.

    Methods:
        __init__(self, tirage, parent=None):
            Initialize the QSpinBoxSearch.

        onvaluechanged(self, value: int):
            Slot for handling the valueChanged signal.

        notify(self, sender, old):
            Notification handler for updating value from sender.
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
        self.setAccelerated(True)
        self.valueChanged.connect(self.onvaluechanged)
        self._tirage.connect_search(self)

    def onvaluechanged(self, value: int):
        """
        Slot for handling the valueChanged signal.

        :param value: The value of the spin box.
        """

        self._tirage.search = value

    def notify(self, sender, old):
        """
        Notification handler for updating the spin box value from the sender.

        :param sender: The object sending the notification.
        :param old: The old value before the update.
        """
        self.valueChanged.disconnect(self.onvaluechanged)
        self.setValue(sender.value)
        self.valueChanged.connect(self.onvaluechanged)
