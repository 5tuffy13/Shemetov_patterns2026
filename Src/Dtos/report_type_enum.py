from enum import Enum
from Src.Core.exception import argument_exception


class report_type_enum(Enum):
    """
    Типы поддерживаемых форматов отчетов
    """

    TXT = 1
    CSV = 2
    MARKDOWN = 3
    XML = 4
    HTML = 5

    @classmethod
    def from_string(cls, value: str) -> "report_type_enum":
        """
        Преобразование строкового наименования в элемент перечисления
        """
        if not isinstance(value, str):
            raise argument_exception("value", "Наименование формата должно быть строкой!")

        normalized = value.strip().upper()
        mapping = {
            "TXT": cls.TXT,
            "TEXT": cls.TXT,
            "CSV": cls.CSV,
            "MD": cls.MARKDOWN,
            "MARKDOWN": cls.MARKDOWN,
            "XML": cls.XML,
            "HTML": cls.HTML,
        }

        if normalized not in mapping:
            raise argument_exception("value", f"Неизвестный формат отчета '{value}'!")

        return mapping[normalized]
