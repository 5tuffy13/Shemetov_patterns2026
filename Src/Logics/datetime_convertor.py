from datetime import date, datetime, time
from typing import Any
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import argument_exception


class datetime_convertor(abstract_convertor):
    """
    Конвертер объектов даты и времени в строковый формат ISO 8601
    """

    SUPPORTED_TYPES = (datetime, date, time)

    def convert(self, source: Any) -> Any:
        """
        Преобразование объекта даты или времени в строку ISO.

        Args:
            source: Объект datetime, date или time

        Returns:
            Строка формата ISO 8601
        """
        if source is None:
            return None

        if isinstance(source, self.SUPPORTED_TYPES):
            return source.isoformat()

        raise argument_exception(
            "source",
            f"Тип '{type(source).__name__}' не поддерживается конвертером даты/времени!"
        )
