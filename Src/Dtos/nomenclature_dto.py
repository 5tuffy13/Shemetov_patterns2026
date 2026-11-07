from typing import Any, Dict
from Src.Core.abstract_dto import abstract_dto
from Src.Core.validator import validator
from Src.Models.nomenclature_model import nomenclature_model


class nomenclature_dto(abstract_dto):
    """
    Структура передачи данных для номенклатуры
    """

    def __init__(self):
        self.__id: str = ""
        self.__name: str = ""
        self.__full_name: str = ""
        self.__group_code: str = ""
        self.__range_code: str = ""

    @property
    def id(self) -> str:
        """
        Идентификатор
        """
        return self.__id

    @id.setter
    def id(self, value: str) -> None:
        validator.validate_type(value, str, field_name="id")
        self.__id = value.strip()

    @property
    def name(self) -> str:
        """
        Краткое наименование
        """
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        validator.validate_type(value, str, field_name="name")
        self.__name = value.strip()

    @property
    def full_name(self) -> str:
        """
        Полное наименование
        """
        return self.__full_name

    @full_name.setter
    def full_name(self, value: str) -> None:
        validator.validate_type(value, str, field_name="full_name")
        self.__full_name = value.strip()

    @property
    def group_code(self) -> str:
        """
        Идентификатор группы номенклатуры
        """
        return self.__group_code

    @group_code.setter
    def group_code(self, value: str) -> None:
        validator.validate_type(value, str, field_name="group_code")
        self.__group_code = value.strip()

    @property
    def range_code(self) -> str:
        """
        Идентификатор единицы измерения
        """
        return self.__range_code

    @range_code.setter
    def range_code(self, value: str) -> None:
        validator.validate_type(value, str, field_name="range_code")
        self.__range_code = value.strip()

    def from_domain_model(self, source: nomenclature_model) -> "nomenclature_dto":
        """
        Создать DTO из доменной модели номенклатуры
        """
        validator.validate_type(source, nomenclature_model, field_name="source")

        dto = nomenclature_dto()
        dto.id = source.id
        dto.name = source.name
        dto.full_name = source.full_name

        if source.group is not None:
            dto.group_code = source.group.id

        if source.range is not None:
            dto.range_code = source.range.id

        return dto

    def from_dict(self, data: Dict[str, Any]) -> "nomenclature_dto":
        """
        Заполнить свойства DTO из словаря
        """
        validator.validate_type(data, dict, field_name="data")
        if "id" in data and data["id"] is not None:
            self.id = str(data["id"])
        if "name" in data and data["name"] is not None:
            self.name = str(data["name"])
        if "full_name" in data and data["full_name"] is not None:
            self.full_name = str(data["full_name"])
        if "group_code" in data and data["group_code"] is not None:
            self.group_code = str(data["group_code"])
        if "range_code" in data and data["range_code"] is not None:
            self.range_code = str(data["range_code"])
        return self
