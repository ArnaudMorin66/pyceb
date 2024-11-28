class IPlaqueNotify:
    def plaque_notify(self, sender, old: int):
        pass


class ITypeNotify[T]:
    def notify(self, sender, old: T):
        pass
