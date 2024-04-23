from abc import abstractmethod, ABC


class DocumentPart(ABC):
    @abstractmethod
    def add_to(self, document):
        raise NotImplementedError
