from abc import ABC, abstractmethod
from typing import Any


class abstract_convertor(ABC):
    """
    Абстрактный класс конвертера данных для сериализации
    """

    @abstractmethod
    def convert(self, source: Any) -> Any:
        """
        Преобразование переданного объекта в сериализуемое представление (словарь или базовый тип)

        Args:
            source: Исходный объект для преобразования

        Returns:
            Сериализуемое представление объекта
        """
        pass
