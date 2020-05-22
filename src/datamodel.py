from enum import Enum
from typing import List, Any


class ModelEventType(Enum):
    ADD, REMOVE, SELECT = range(3)


class ModelEvent:
    type: ModelEventType

    def __init__(self, type: ModelEventType, data=None):
        self.type = type
        self.data = data


class DataModel:
    selected_instance: str
    selected_instances: List[str]

    def __init__(self, data):
        self.selected_instances = []
        self.selected_instance = next(iter(data['images']))
        self.data = data
        self.observers = []

    def add(self, identifier):
        if identifier not in self.selected_instances:
            self.selected_instances.append(identifier)
            self._notify_observers(ModelEvent(ModelEventType.ADD, data=identifier))

    def select(self, identifier):
        if identifier != self.selected_instance:
            self.selected_instance = identifier
            self._notify_observers(ModelEvent(ModelEventType.SELECT, data=identifier))

    def remove(self, identifier):
        if identifier in self.selected_instances:
            self.selected_instances.remove(identifier)
            self._notify_observers(ModelEvent(ModelEventType.REMOVE, data=identifier))

    def _notify_observers(self, event: ModelEvent):
        for observer in self.observers:
            observer.notify(event)