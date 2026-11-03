from abc import ABC, abstractmethod
from typing import Any
from Src.Core.abstract_convertor import abstract_convertor


class abstract_convert_factory(ABC):
    """
    Абстрактная фабрика для создания и подбора конвертеров данных
    """

    @abstractmethod
    def create(self, source: Any) -> abstract_convertor:
        """
        Фабричный метод создания конвертера для целевого типа или объекта.

        Args:
            source: Класс или экземпляр целевого объекта

        Returns:
            Экземпляр соответствующего конвертера
        """
        pass
