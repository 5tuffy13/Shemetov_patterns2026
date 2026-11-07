from typing import Any, Dict
from Src.Core.abstract_dto import abstract_dto
from Src.Core.validator import validator
from Src.Models.receipt_row_model import receipt_row_model


class receipt_row_dto(abstract_dto):
    """
    Структура передачи данных для строки технологической карты
    """

    def __init__(self):
        self.__id: str = ""
        self.__name: str = ""
        self.__gross: float = 0.0
        self.__net: float = 0.0
        self.__nomenclature_code: str = ""
        self.__receipt_code: str = ""

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
    def gross(self) -> float:
        return self.__gross

    @gross.setter
    def gross(self, value: int | float) -> None:
        validator.validate_number(value, positive_only=True, field_name="gross")
        self.__gross = float(value)

    @property
    def net(self) -> float:
        return self.__net

    @net.setter
    def net(self, value: int | float) -> None:
        validator.validate_number(value, positive_only=True, field_name="net")
        self.__net = float(value)

    @property
    def nomenclature_code(self) -> str:
        return self.__nomenclature_code

    @nomenclature_code.setter
    def nomenclature_code(self, value: str) -> None:
        validator.validate_type(value, str, field_name="nomenclature_code")
        self.__nomenclature_code = value.strip()

    @property
    def receipt_code(self) -> str:
        return self.__receipt_code

    @receipt_code.setter
    def receipt_code(self, value: str) -> None:
        validator.validate_type(value, str, field_name="receipt_code")
        self.__receipt_code = value.strip()

    def from_domain_model(self, source: receipt_row_model) -> "receipt_row_dto":
        """
        Создать DTO из доменной строки рецепта
        """
        validator.validate_type(source, receipt_row_model, field_name="source")

        dto = receipt_row_dto()
        dto.id = source.id
        dto.name = source.name
        dto.gross = source.gross
        dto.net = source.net

        if source.nomenclature is not None:
            dto.nomenclature_code = source.nomenclature.id

        if source.receipt is not None:
            dto.receipt_code = source.receipt.id

        return dto

    def from_dict(self, data: Dict[str, Any]) -> "receipt_row_dto":
        """
        Заполнить свойства DTO из словаря
        """
        validator.validate_type(data, dict, field_name="data")
        if "id" in data and data["id"] is not None:
            self.id = str(data["id"])
        if "name" in data and data["name"] is not None:
            self.name = str(data["name"])
        if "gross" in data and data["gross"] is not None:
            self.gross = data["gross"]
        if "net" in data and data["net"] is not None:
            self.net = data["net"]
        if "nomenclature_code" in data and data["nomenclature_code"] is not None:
            self.nomenclature_code = str(data["nomenclature_code"])
        if "receipt_code" in data and data["receipt_code"] is not None:
            self.receipt_code = str(data["receipt_code"])
        return self
