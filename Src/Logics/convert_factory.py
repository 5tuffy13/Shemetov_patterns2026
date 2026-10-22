import json
from datetime import date, datetime, time
from typing import Any, Dict, Optional, Set, Type
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_reference import abstract_reference
from Src.Core.exception import argument_exception
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor


class convert_factory:
    """
    Фабрика конвертации объектов в сериализуемые структуры данных (словари и списки)
    """

    def __init__(self):
        """
        Инициализация фабрики и регистрация базовых конвертеров
        """
        self.__basic_convertor = basic_convertor()
        self.__datetime_convertor = datetime_convertor()
        self.__reference_convertor = reference_convertor(factory=self)

        # Реестр сопоставления типов данных и обработчиков
        self.__converters_map: Dict[Type, abstract_convertor] = {
            int: self.__basic_convertor,
            float: self.__basic_convertor,
            str: self.__basic_convertor,
            bool: self.__basic_convertor,
            datetime: self.__datetime_convertor,
            date: self.__datetime_convertor,
            time: self.__datetime_convertor,
        }

    @property
    def basic(self) -> basic_convertor:
        return self.__basic_convertor

    @property
    def datetime(self) -> datetime_convertor:
        return self.__datetime_convertor

    @property
    def reference(self) -> reference_convertor:
        return self.__reference_convertor

    def get_convertor(self, target_type: Type) -> Optional[abstract_convertor]:
        """
        Фабричный метод получения конвертера по типу объекта

        Args:
            target_type: Класс целевого объекта

        Returns:
            Экземпляр соответствующего конвертера
        """
        if not isinstance(target_type, type):
            raise argument_exception("target_type", "Переданный аргумент должен являться типом!")

        if target_type in self.__converters_map:
            return self.__converters_map[target_type]

        if issubclass(target_type, abstract_reference):
            return self.__reference_convertor

        for registered_type, conv in self.__converters_map.items():
            if issubclass(target_type, registered_type):
                return conv

        return None

    def convert(self, source: Any, visited: Optional[Set[int]] = None) -> Any:
        """
        Преобразование произвольного объекта любой сложности в структуру словарей/списков

        Args:
            source: Исходный объект любого типа
            visited: Множество посещенных объектов для предотвращения циклических ссылок

        Returns:
            Сериализуемая структура (словарь, список или базовый тип)
        """
        if source is None:
            return None

        # Проверка базовых типов через конвертер примитивов
        if isinstance(source, (int, float, str, bool)):
            return self.__basic_convertor.convert(source)

        # Проверка даты и времени
        if isinstance(source, (datetime, date, time)):
            return self.__datetime_convertor.convert(source)

        # Проверка доменной модели
        if isinstance(source, abstract_reference):
            return self.__reference_convertor.convert(source, visited=visited)

        # Проверка коллекций
        if isinstance(source, (list, tuple, set)):
            return [self.convert(item, visited=visited) for item in source]

        # Проверка словаря
        if isinstance(source, dict):
            return {str(k): self.convert(v, visited=visited) for k, v in source.items()}

        # Для прочих объектов пробуем сериализацию строкой
        return str(source)

    def serialize(self, source: Any, indent: Optional[int] = None) -> str:
        """
        Формирование итоговой JSON-строки по исходному объекту

        Args:
            source: Объект для сериализации
            indent: Число пробелов для форматирования JSON

        Returns:
            Строка формата JSON
        """
        data = self.convert(source)
        return json.dumps(data, ensure_ascii=False, indent=indent)
