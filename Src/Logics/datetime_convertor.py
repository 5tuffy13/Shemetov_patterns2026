from datetime import date, datetime, time
from typing import Any
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import argument_exception


class datetime_convertor(abstract_convertor):
    """
    Конвертер объектов даты и времени в строковое ISO-представление
    """

    SUPPORTED_TYPES = (datetime, date, time)

    def convert(self, source: Any) -> Any:
        """
        Преобразование объекта даты или времени в формат ISO.

        Args:
            source: Объект datetime, date, time или словарь с такими значениями

        Returns:
            Строка в формате ISO либо словарь со строковыми датами
        """
        if source is None:
            return None

        if isinstance(source, self.SUPPORTED_TYPES):
            return source.isoformat()

        if isinstance(source, dict):
            result = {}
            for key, value in source.items():
                if value is not None and not isinstance(value, self.SUPPORTED_TYPES):
                    raise argument_exception("source", f"Значение ключа '{key}' не является объектом даты/времени!")
                result[str(key)] = value.isoformat() if value is not None else None
            return result

        raise argument_exception("source", f"Тип '{type(source).__name__}' не поддерживается конвертером даты/времени!")
