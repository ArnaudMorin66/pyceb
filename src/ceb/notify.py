from typing import List


class IPlaqueNotify:
    def plaque_notify(self, new, old: int):
        pass

class ISearchNotify:
    def search_notify(self, new: int, old: int):
        pass

class ITypeNotify[T]:
    def turn_notify(self, new: T, old: T):
        pass

class ObservableSearch:
    _observers: List[ISearchNotify] = []
    def __init__(self, value=0):
        self._value = value
        self._observers = []

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if self._value != new_value:
            old_value = self._value
            self._value = new_value
            self._notify_observers(new_value, old_value)

    def add_observer(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(self, new_value, old_value):
        for observer in self._observers:
            observer.search_notify(new_value.value, old_value)



