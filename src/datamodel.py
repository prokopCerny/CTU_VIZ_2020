from enum import Enum


class ModelEventType(Enum):
    ADD, REMOVE = range(2)


class ModelEvent:
    type: ModelEventType

    def __init__(self, type: ModelEventType, data=None):
        self.type = type
        self.data = data


class DataModel:
    def __init__(self, data):
        self.selected = []
        self.data = data
        self.observers = []

    def select(self, identifier):
        if identifier not in self.selected:
            self.selected.append(identifier)
            self._notify_observers(ModelEvent(ModelEventType.ADD, data=identifier))

    def remove(self, identifier):
        if identifier in self.selected:
            self.selected.remove(identifier)
            self._notify_observers(ModelEvent(ModelEventType.REMOVE, data=identifier))

    def _notify_observers(self, event: ModelEvent):
        for observer in self.observers:
            observer.notify(event)