from enum import Enum
from typing import Optional
from Src.Core.exception import argument_exception


class sort_direction_enum(Enum):
    """
    Перечисление направлений сортировки записей журнала
    """

    ASC = "ASC"
    DESC = "DESC"

    @classmethod
    def from_string(cls, value: Optional[str]) -> "sort_direction_enum":
        """
        Преобразование строкового значения в направление сортировки
        """
        if value is None:
            return cls.DESC

        if not isinstance(value, str):
            raise argument_exception("value", "Направление сортировки должно быть строкой!")

        normalized = value.strip().upper()
        if not normalized:
            return cls.DESC

        for item in cls:
            if item.name == normalized or item.value == normalized:
                return item

        raise argument_exception("value", f"Неизвестное направление сортировки '{value}'!")
