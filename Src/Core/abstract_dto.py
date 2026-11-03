from abc import ABC, abstractmethod
from Src.Core.abstract_reference import abstract_reference


class abstract_dto(ABC):
    """
    Абстрактный класс для структур передачи данных
    """

    @abstractmethod
    def from_domain_model(self, source: abstract_reference) -> "abstract_dto":
        """
        Фабричный метод создания DTO из доменной модели
        """
        pass
