from typing import Any, Dict, List
from Src.Core.abstract_dto import abstract_dto
from Src.Core.validator import validator
from Src.Dtos.receipt_row_dto import receipt_row_dto
from Src.Models.receipt_model import receipt_model


class receipt_dto(abstract_dto):
    """
    Структура передачи данных для технологической карты
    """

    def __init__(self):
        self.__id: str = ""
        self.__name: str = ""
        self.__portions: int = 1
        self.__cooking_time: int = 0
        self.__rows: List[receipt_row_dto] = []

    @property
    def id(self) -> str:
        return self.__id

    @id.setter
    def id(self, value: str) -> None:
        validator.validate_type(value, str, field_name="id")
        self.__id = value.strip()

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        validator.validate_type(value, str, field_name="name")
        self.__name = value.strip()

    @property
    def portions(self) -> int:
        return self.__portions

    @portions.setter
    def portions(self, value: int) -> None:
        validator.validate_type(value, int, field_name="portions")
        self.__portions = value

    @property
    def cooking_time(self) -> int:
        return self.__cooking_time

    @cooking_time.setter
    def cooking_time(self, value: int) -> None:
        validator.validate_type(value, int, field_name="cooking_time")
        self.__cooking_time = value

    @property
    def rows(self) -> List[receipt_row_dto]:
        return self.__rows

    @rows.setter
    def rows(self, value: list) -> None:
        validator.validate_type(value, list, field_name="rows")
        self.__rows = value

    def from_domain_model(self, source: receipt_model) -> "receipt_dto":
        """
        Создать DTO из доменной модели технологической карты
        """
        validator.validate_type(source, receipt_model, field_name="source")

        dto = receipt_dto()
        dto.id = source.id
        dto.name = source.name
        dto.portions = source.portions
        dto.cooking_time = source.cooking_time

        row_builder = receipt_row_dto()
        dto.rows = [row_builder.from_domain_model(row) for row in source.rows]

        return dto

    def from_dict(self, data: Dict[str, Any]) -> "receipt_dto":
        """
        Заполнить свойства DTO из словаря
        """
        validator.validate_type(data, dict, field_name="data")
        if "id" in data and data["id"] is not None:
            self.id = str(data["id"])
        if "name" in data and data["name"] is not None:
            self.name = str(data["name"])
        if "portions" in data and data["portions"] is not None:
            self.portions = int(data["portions"])
        if "cooking_time" in data and data["cooking_time"] is not None:
            self.cooking_time = int(data["cooking_time"])
        if "rows" in data and isinstance(data["rows"], list):
            parsed_rows = []
            for r in data["rows"]:
                if isinstance(r, dict):
                    parsed_rows.append(receipt_row_dto().from_dict(r))
                elif isinstance(r, receipt_row_dto):
                    parsed_rows.append(r)
            self.rows = parsed_rows
        return self
