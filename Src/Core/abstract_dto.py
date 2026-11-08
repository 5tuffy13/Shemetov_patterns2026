from abc import ABC, abstractmethod
from typing import Any, Dict
from Src.Core.abstract_reference import abstract_reference


class abstract_dto(ABC):
    """
    Базовый класс для всех структур передачи данных (DTO)
    """

    @property
    def type(self) -> str:
        """
        Полное квалифицированное имя класса структуры DTO
        """
        return f"{self.__class__.__module__}.{self.__class__.__qualname__}"

    @abstractmethod
    def from_domain_model(self, source: abstract_reference) -> "abstract_dto":
        """
        Фабричный метод создания DTO из доменной модели
        """
        pass

    @abstractmethod
    def from_dict(self, data: Dict[str, Any]) -> "abstract_dto":
        """
        Заполнить поля DTO из переданного словаря
        """
        pass
