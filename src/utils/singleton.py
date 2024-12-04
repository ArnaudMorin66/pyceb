
def singleton(class_):
    """
    Decorator to make a class a singleton. Ensures that only one instance of the class exists.

    :param class_: The class to be turned into a singleton.
    :type class_: type
    :return: The singleton instance of the class.
    :rtype: type
    """
    instances = {}

    def get_instance(*args, **kwargs):
        """
        Retourne l'instance unique de la classe.

        :param args: Arguments positionnels pour l'initialisation de la classe.
        :param kwargs: Arguments nommés pour l'initialisation de la classe.
        :return: L'instance unique de la classe.
        """
        if class_ not in instances:
            kl = class_(*args, **kwargs)
            instances[class_] = kl
        return instances[class_]

    return get_instance

class MetaSingleton(type):
    """
    Metaclass pour créer des singletons. Assure qu'une seule instance de la classe existe.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Retourne l'instance unique de la classe.

        :param args: Arguments positionnels pour l'initialisation de la classe.
        :param kwargs: Arguments nommés pour l'initialisation de la classe.
        :return: L'instance unique de la classe.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
