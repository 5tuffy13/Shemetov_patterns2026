from enum import Enum
from Src.Core.exception import argument_exception


class log_level_enum(Enum):
    """
    Перечисление уровней значимости записей журнала событий
    """

    ERROR = "ERROR"
    INFO = "INFO"
    DEBUG = "DEBUG"

    @classmethod
    def from_string(cls, value: str) -> "log_level_enum":
        """
        Преобразование строкового наименования в уровень логирования
        """
        if not isinstance(value, str):
            raise argument_exception("value", "Уровень логирования должен быть строкой!")

        normalized = value.strip().upper()
        for item in cls:
            if item.name == normalized or item.value == normalized:
                return item

        raise argument_exception("value", f"Неизвестный уровень логирования '{value}'!")
