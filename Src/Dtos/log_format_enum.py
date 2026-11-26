from enum import Enum
from Src.Core.exception import argument_exception


class log_format_enum(Enum):
    """
    Перечисление поддерживаемых форматов выгрузки журнала событий
    """

    JSON = "JSON"
    TXT = "TXT"
    CSV = "CSV"
    MARKDOWN = "MARKDOWN"

    @classmethod
    def from_string(cls, value: str) -> "log_format_enum":
        """
        Преобразование строкового обозначения в формат выгрузки лога
        """
        if not isinstance(value, str):
            raise argument_exception("value", "Формат экспорта лога должен быть строкой!")

        normalized = value.strip().upper()
        mapping = {
            "JSON": cls.JSON,
            "TXT": cls.TXT,
            "TEXT": cls.TXT,
            "CSV": cls.CSV,
            "MD": cls.MARKDOWN,
            "MARKDOWN": cls.MARKDOWN,
        }

        if normalized not in mapping:
            raise argument_exception("value", f"Неизвестный формат экспорта лога '{value}'!")

        return mapping[normalized]
