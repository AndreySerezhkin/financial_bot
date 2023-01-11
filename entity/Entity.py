from abc import ABC, abstractmethod


class EntityProcess(ABC):

    @abstractmethod
    def create_process():
        pass

    @abstractmethod
    def read_process():
        pass

    @abstractmethod
    def update_process():
        pass

    @abstractmethod
    def delete_process():
        pass
