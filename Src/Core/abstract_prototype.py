from abc import ABC, abstractmethod
from typing import Any, List
from Src.Dtos.filter_dto import filter_dto


class abstract_prototype(ABC):
    """
    Абстрактный класс паттерна Прототип для фильтрации и клонирования наборов данных
    """

    @property
    @abstractmethod
    def data(self) -> List[Any]:
        """
        Инкапсулированная коллекция объектов
        """
        pass

    @abstractmethod
    def clone(self, filter_instance: filter_dto) -> "abstract_prototype":
        """
        Создать независимый отфильтрованный клон текущего прототипа
        """
        pass
