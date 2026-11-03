from datetime import date, datetime, time
from typing import Dict, Type
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_reference import abstract_reference
from Src.Core.exception import argument_exception
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.dictionary_convertor import dictionary_convertor
from Src.Logics.list_convertor import list_convertor
from Src.Logics.reference_convertor import reference_convertor


class convert_factory(abstract_convert_factory):
    """
    Фабрика для создания и подбора конвертеров данных
    """

    def __init__(self):
        self.__basic_convertor = basic_convertor()
        self.__datetime_convertor = datetime_convertor()
        self.__list_convertor = list_convertor(factory=self)
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
        }

    def create(self, target_type: Type) -> abstract_convertor:
        """
        Фабричный метод подбора конвертера по целевому типу данных.

        Args:
            target_type: Класс целевого объекта

        Returns:
            Экземпляр соответствующего конвертера
        """
        if not isinstance(target_type, type):
            raise argument_exception("target_type", "Аргумент должен являться типом!")

        if target_type in self.__mapping:
            return self.__mapping[target_type]

        if issubclass(target_type, abstract_reference):
            return self.__reference_convertor

        for registered_type, conv in self.__mapping.items():
            if issubclass(target_type, registered_type):
                return conv

        raise argument_exception(
            "target_type",
            f"Для типа '{target_type.__name__}' конвертер не зарегистрирован!"
        )
