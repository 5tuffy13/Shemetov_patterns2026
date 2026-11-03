from abc import ABC, abstractmethod
from typing import Type
from Src.Core.abstract_convertor import abstract_convertor


class abstract_convert_factory(ABC):
    """
    Абстрактная фабрика для создания и подбора конвертеров данных
    """

    @abstractmethod
    def create(self, target_type: Type) -> abstract_convertor:
        """
        Фабричный метод создания конвертера для целевого типа данных.

        Args:
            target_type: Класс целевого объекта

        Returns:
            Экземпляр соответствующего конвертера
        """
        pass
