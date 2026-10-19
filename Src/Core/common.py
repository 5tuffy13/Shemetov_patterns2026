from typing import Any, List
from Src.Core.abstract_reference import abstract_reference
from Src.Core.exception import argument_exception
from Src.Core.validator import validator
from Src.Dtos.entity_description_header_dto import entity_description_header_dto
from Src.Dtos.entity_description_table_dto import entity_description_table_dto


class common:
    """
    Набор общих статических методов рефлексии и интроспекции доменных моделей
    """

    @staticmethod
    def get_fields(source: Any, is_common: bool = False) -> List[str]:
        """
        Получить список публичных свойств переданного объекта.

        Args:
            source: Исходный объект для интроспекции
            is_common: Флаг исключения коллекций (списков и словарей)

        Returns:
            Список наименований свойств
        """
        if source is None:
            raise argument_exception("source", "Некорректно передан объект для интроспекции!")

        attributes = [name for name in dir(source) if not name.startswith("_")]
        result = []

        for attr_name in attributes:
            class_attr = getattr(source.__class__, attr_name, None)

            if isinstance(class_attr, property):
                try:
                    value = getattr(source, attr_name)
                except Exception:
                    continue

                # Исключение списков и словарей при запросе скалярных свойств
                if is_common and (isinstance(value, (dict, list, set, tuple))):
                    continue

                result.append(attr_name)

        return result

    @staticmethod
    def get_entity_header(source: abstract_reference) -> List[entity_description_header_dto]:
        """
        Получить строковое описание скалярных полей доменной сущности (заголовочная часть).

        Args:
            source: Доменная модель

        Returns:
            Список DTO элементов описания полей
        """
        if source is None:
            raise argument_exception("source", "Некорректно передан объект сущности!")

        result: List[entity_description_header_dto] = []
        field_names = common.get_fields(source, is_common=True)

        for field_name in field_names:
            try:
                raw_value = getattr(source, field_name)
                str_value = str(raw_value) if raw_value is not None else ""
            except Exception:
                str_value = ""

            result.append(entity_description_header_dto(field=field_name, value=str_value))

        return result

    @staticmethod
    def get_entity_table(source: abstract_reference) -> List[entity_description_table_dto]:
        """
        Получить табличную часть для агрегата.
        Ищет коллекционные свойства (списки дочерних строк), формируя DTO для каждой строки.

        Args:
            source: Агрегатная доменная модель

        Returns:
            Список DTO строк табличной части
        """
        if source is None:
            raise argument_exception("source", "Некорректно передан объект сущности!")

        result: List[entity_description_table_dto] = []
        field_names = common.get_fields(source, is_common=False)

        # Поиск первого непустого свойства-списка
        list_field = None
        for name in field_names:
            val = getattr(source, name, None)
            if isinstance(val, list) and len(val) > 0:
                list_field = val
                break

        if not list_field:
            return result

        for item in list_field:
            headers = common.get_entity_header(item)
            columns = [header.field for header in headers]
            values = [header.value for header in headers]
            result.append(entity_description_table_dto(columns=columns, values=values))

        return result
