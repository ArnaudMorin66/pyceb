from typing import Callable


class Notification:
    """
    Classe de base pour la gestion des signaux et des observateurs.
    """

    def __init__(self):
        """
        Initialise une nouvelle instance de SignalBase.
        """
        self._observers = set()

    def connect(self, observer:Callable):
        """
        Connecte un observateur au signal.

        :param observer: La fonction observatrice à connecter.
        """
        self._observers.add(observer)

    def disconnect(self, observer:Callable):
        """
        Déconnecte un observateur du signal.

        :param observer: La fonction observatrice à déconnecter.
        """
        if self.is_connect(observer):
            self._observers.remove(observer)

    def disconnect_all(self):
        """
        Déconnecte tous les observateurs du signal.
        """
        self._observers.clear()

    def is_connect(self, observer: Callable) -> bool:
        """
        Vérifie si un observateur est connecté au signal.

        :param observer: La fonction observatrice à vérifier.
        :return: True si l'observateur est connecté, sinon False.
        """
        return observer in self._observers

    def has_connect(self):
        """
        Vérifie s'il y a des observateurs connectés au signal.

        :return: True s'il y a des observateurs connectés, sinon False.
        """
        return len(self._observers) > 0

    def emit(self, *args, **kwargs):
        """
        Émet le signal à tous les observateurs connectés.

        :param args: Arguments positionnels à passer aux observateurs.
        :param kwargs: Arguments nommés à passer aux observateurs.
        """
        for observer in self._observers:
            observer(*args, **kwargs)

