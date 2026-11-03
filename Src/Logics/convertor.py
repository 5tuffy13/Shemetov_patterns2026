from typing import Any, Optional
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Logics.convert_factory import convert_factory


class convertor:
    """
    Фасад для сериализации и десериализации данных
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(convertor, cls).__new__(cls)
            cls._instance.__factory = convert_factory()
        return cls._instance

    @property
    def factory(self) -> abstract_convert_factory:
        """
        Фабрика конвертеров данных
        """
        return self.__factory

    def serialize(self, source: Any, field_name: str = "result") -> dict:
        """
        Сериализовать объект в словарь
        """
        conv = self.__factory.create(source)
        return conv.serialize(field_name, source)

    def deserialize(self, source: dict) -> object:
        """
        Десериализовать словарь в объект
        """
        pass
