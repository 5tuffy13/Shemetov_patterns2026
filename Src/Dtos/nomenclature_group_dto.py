from typing import Any, Dict
from Src.Core.abstract_dto import abstract_dto
from Src.Core.validator import validator
from Src.Models.nomenclature_group_model import nomenclature_group_model


class nomenclature_group_dto(abstract_dto):
    """
    Структура передачи данных для группы номенклатуры
    """

    def __init__(self):
        self.__id: str = ""
        self.__name: str = ""

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
        Наименование группы
        """
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        validator.validate_type(value, str, field_name="name")
        self.__name = value.strip()

    def from_domain_model(self, source: nomenclature_group_model) -> "nomenclature_group_dto":
        """
        Создать DTO из доменной модели группы номенклатуры
        """
        validator.validate_type(source, nomenclature_group_model, field_name="source")

        dto = nomenclature_group_dto()
        dto.id = source.id
        dto.name = source.name
        return dto

    def from_dict(self, data: Dict[str, Any]) -> "nomenclature_group_dto":
        """
        Заполнить свойства DTO из словаря
        """
        validator.validate_type(data, dict, field_name="data")
        if "id" in data and data["id"] is not None:
            self.id = str(data["id"])
        if "name" in data and data["name"] is not None:
            self.name = str(data["name"])
        return self
