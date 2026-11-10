from datetime import date, datetime, time
from typing import Any, Dict, Type
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_dto import abstract_dto
from Src.Core.abstract_reference import abstract_reference
from Src.Core.exception import argument_exception
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.dictionary_convertor import dictionary_convertor
from Src.Logics.domain_convertor import domain_convertor
from Src.Logics.list_convertor import list_convertor
from Src.Logics.mapping_factory import mapping_factory
from Src.Logics.reference_convertor import reference_convertor


class convert_factory(abstract_convert_factory):
    """
    Фабрика для создания и подбора специализированных конвертеров данных
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(convert_factory, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_convert_factory__initialized", False):
            return

        super().__init__()

        self.__basic_convertor = basic_convertor()
        self.__datetime_convertor = datetime_convertor()
        self.__mapping_factory = mapping_factory()
        self.__domain_convertor = domain_convertor(self, self.__mapping_factory)
        self.__list_convertor = list_convertor(convert_factory=self, mapping_factory=self.__mapping_factory)
        self.__dictionary_convertor = dictionary_convertor(factory=self)
        self.__reference_convertor = reference_convertor(factory=self)

        # Реестр привязки типов данных к конвертерам
        self.__mapping: Dict[Type, abstract_convertor] = {
            int: self.__basic_convertor,
            float: self.__basic_convertor,
            str: self.__basic_convertor,
            bool: self.__basic_convertor,
            datetime: self.__datetime_convertor,
            date: self.__datetime_convertor,
            time: self.__datetime_convertor,
            list: self.__list_convertor,
            tuple: self.__list_convertor,
            set: self.__list_convertor,
            dict: self.__dictionary_convertor,
            abstract_dto: self.__domain_convertor,
            abstract_reference: self.__domain_convertor,
        }

        self.__initialized = True

    @property
    def mapping_factory(self) -> mapping_factory:
        return self.__mapping_factory

    @property
    def domain_convertor(self) -> domain_convertor:
        return self.__domain_convertor

    @property
    def list_convertor(self) -> list_convertor:
        return self.__list_convertor

    @property
    def dictionary_convertor(self) -> dictionary_convertor:
        return self.__dictionary_convertor

    @property
    def reference_convertor(self) -> reference_convertor:
        return self.__reference_convertor

    def create(self, source: Any) -> abstract_convertor:
        """
        Фабричный метод подбора конвертера по целевому типу или объекту.

        Args:
            source: Класс целевого объекта или экземпляр

        Returns:
            Экземпляр соответствующего конвертера
        """
        if source is None:
            return self.__basic_convertor

        target_type = source if isinstance(source, type) else type(source)

        if target_type in self.__mapping:
            return self.__mapping[target_type]

        if issubclass(target_type, abstract_dto):
            return self.__domain_convertor

        if issubclass(target_type, abstract_reference):
            return self.__domain_convertor

        for registered_type, conv in self.__mapping.items():
            if issubclass(target_type, registered_type):
                return conv

        raise argument_exception(
            "source",
            f"Для типа '{target_type.__name__}' конвертер не зарегистрирован!"
        )
