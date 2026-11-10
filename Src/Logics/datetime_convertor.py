from datetime import date, datetime, time
from typing import Any, Optional
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import argument_exception


class datetime_convertor(abstract_convertor):
    """
    Конвертер объектов даты и времени в строковый формат ISO 8601 и обратно
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

    def deserialize(self, source: Any, target_type: Optional[type] = None) -> Any:
        """
        Восстановление объекта даты/времени из строки ISO.
        """
        if source is None:
            return None

        if isinstance(source, self.SUPPORTED_TYPES):
            return source

        if not isinstance(source, str):
            raise argument_exception(
                "source",
                f"Ожидается строка формата ISO для даты/времени, получено '{type(source).__name__}'"
            )

        clean_val = source.strip()
        try:
            if target_type is time:
                return time.fromisoformat(clean_val)
            if target_type is date:
                return date.fromisoformat(clean_val)
            if target_type is datetime:
                return datetime.fromisoformat(clean_val)

            # Автоматическое определение по длине и разделителям
            if "T" in clean_val or " " in clean_val:
                return datetime.fromisoformat(clean_val)
            if clean_val.count("-") == 2:
                return date.fromisoformat(clean_val)
            if clean_val.count(":") >= 1:
                return time.fromisoformat(clean_val)

            return datetime.fromisoformat(clean_val)
        except Exception as ex:
            raise argument_exception(
                "source",
                f"Не удалось преобразовать строку '{clean_val}' в объект даты/времени: {ex}"
            )
