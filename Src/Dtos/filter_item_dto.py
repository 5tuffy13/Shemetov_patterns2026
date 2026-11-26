from typing import Any, Dict
from Src.Core.validator import validator
from Src.Dtos.filter_type_enum import filter_type_enum


class filter_item_dto:
    """
    Элемент условия фильтрации с описанием поля, операции и значения
    """

    def __init__(
        self,
        field_name: str = "name",
        filter_type: filter_type_enum = filter_type_enum.EQUALS,
        value: Any = "",
    ):
        """
        Инициализация элемента фильтра
        """
        self.__field_name: str = ""
        self.__filter_type: filter_type_enum = filter_type_enum.EQUALS
        self.__value: Any = value

        self.field_name = field_name
        self.filter_type = filter_type
        self.value = value

    @property
    def field_name(self) -> str:
        """
        Имя проверяемого поля
        """
        return self.__field_name

    @field_name.setter
    def field_name(self, value: str):
        """
        Сеттер имени поля
        """
        validator.validate(value, str, 100, field_name="field_name")
        self.__field_name = value.strip()

    @property
    def filter_type(self) -> filter_type_enum:
        """
        Тип операции фильтрации
        """
        return self.__filter_type

    @filter_type.setter
    def filter_type(self, value: Any):
        """
        Сеттер типа операции
        """
        if isinstance(value, filter_type_enum):
            self.__filter_type = value
        elif isinstance(value, str):
            self.__filter_type = filter_type_enum.from_string(value)
        else:
            self.__filter_type = filter_type_enum.EQUALS

    @property
    def value(self) -> Any:
        """
        Значение критерия фильтрации
        """
        return self.__value

    @value.setter
    def value(self, val: Any):
        """
        Сеттер значения критерия
        """
        self.__value = val

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "filter_item_dto":
        """
        Фабричный метод создания DTO из словаря
        """
        validator.validate(data, dict, field_name="data")
        field_name = data.get("field_name") or data.get("field") or "name"
        filter_type_val = data.get("filter_type") or data.get("type") or "EQUALS"
        value = data.get("value", "")
        return cls(field_name=field_name, filter_type=filter_type_val, value=value)
