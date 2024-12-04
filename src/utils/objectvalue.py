from utils import ObsEvent


class ObjectValue[T]:
    """
    Classe SignalObject qui hérite de SignalBase et gère une valeur de type g��nérique T.
    Émet un signal lorsque la valeur change.
    """
    _value: T
    _event: ObsEvent

    def __init__(self, value: T | None = None):
        """
        Initialise une nouvelle instance de SignalObject.

        :param value: La valeur initiale de l'objet, de type T ou None.
        """
        super().__init__()
        self._event = ObsEvent()
        if value is not None:
            self._value = value

    # noinspection PyPep8Naming
    @property
    def event(self):
        """
        Retourne le signal de changement de la valeur.

        :return: Le signal de changement de la valeur.
        """
        return self._event

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
        self.event.emit(self, old_value)

    def __repr__(self):
        """
        Retourne une représentation sous forme de chaîne de la valeur de l'objet.

        :return: La valeur de l'objet sous forme de chaîne.
        """
        return str(self._value)
