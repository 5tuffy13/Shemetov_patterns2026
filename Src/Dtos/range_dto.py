from typing import Any, Dict
from Src.Core.abstract_dto import abstract_dto
from Src.Core.validator import validator
from Src.Models.range_model import range_model


class range_dto(abstract_dto):
    """
    Структура передачи данных для единицы измерения
    """

    def __init__(self):
        self.__id: str = ""
        self.__name: str = ""
        self.__coeff: int | float = 1
        self.__base_code: str = ""

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
        Наименование
        """
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        validator.validate_type(value, str, field_name="name")
        self.__name = value.strip()

    @property
    def coeff(self) -> int | float:
        """
        Коэффициент пересчета
        """
        return self.__coeff

    @coeff.setter
    def coeff(self, value: int | float) -> None:
        validator.validate_number(value, positive_only=True, field_name="coeff")
        self.__coeff = value

    @property
    def base_code(self) -> str:
        """
        Идентификатор базовой единицы измерения
        """
        return self.__base_code

    @base_code.setter
    def base_code(self, value: str) -> None:
        validator.validate_type(value, str, field_name="base_code")
        self.__base_code = value.strip()

    def from_domain_model(self, source: range_model) -> "range_dto":
        """
        Создать DTO из доменной модели единицы измерения
        """
        validator.validate_type(source, range_model, field_name="source")

        dto = range_dto()
        dto.id = source.id
        dto.name = source.name
        dto.coeff = source.coeff

        if source.base_range is not None and source.base_range is not source:
            dto.base_code = source.base_range.id
        else:
            dto.base_code = ""

        return dto

    def from_dict(self, data: Dict[str, Any]) -> "range_dto":
        """
        Заполнить свойства DTO из словаря
        """
        validator.validate_type(data, dict, field_name="data")
        if "id" in data and data["id"] is not None:
            self.id = str(data["id"])
        if "name" in data and data["name"] is not None:
            self.name = str(data["name"])
        if "coeff" in data and data["coeff"] is not None:
            self.coeff = data["coeff"]
        if "base_code" in data and data["base_code"] is not None:
            self.base_code = str(data["base_code"])
        return self
