from enum import Enum


class filter_type_enum(Enum):
    """
    Перечисление поддерживаемых операций фильтрации данных
    """
    EQUALS = "EQUALS"
    LIKE = "LIKE"
    GREATER = "GREATER"
    LESS = "LESS"
    GREATER_OR_EQUAL = "GREATER_OR_EQUAL"
    LESS_OR_EQUAL = "LESS_OR_EQUAL"

    @classmethod
    def from_string(cls, value: str) -> "filter_type_enum":
        """
        Преобразование строкового значения в элемент перечисления
        """
        if not value:
            return cls.EQUALS

        clean_val = str(value).strip().upper()
        # Синонимы для удобства
        aliases = {
            "EQ": cls.EQUALS,
            "EQUAL": cls.EQUALS,
            "EQUALS": cls.EQUALS,
            "LIKE": cls.LIKE,
            "CONTAINS": cls.LIKE,
            "GT": cls.GREATER,
            "GREATER": cls.GREATER,
            "LT": cls.LESS,
            "LESS": cls.LESS,
            "GTE": cls.GREATER_OR_EQUAL,
            "GREATER_OR_EQUAL": cls.GREATER_OR_EQUAL,
            "LTE": cls.LESS_OR_EQUAL,
            "LESS_OR_EQUAL": cls.LESS_OR_EQUAL,
        }
        if clean_val in aliases:
            return aliases[clean_val]

        for item in cls:
            if item.name == clean_val or item.value == clean_val:
                return item

        return cls.EQUALS
