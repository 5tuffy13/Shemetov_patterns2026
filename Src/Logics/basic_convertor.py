from typing import Any
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import argument_exception


class basic_convertor(abstract_convertor):
    """
    Конвертер базовых типов данных (числовые, строковые, логические)
    """

    SUPPORTED_TYPES = (int, float, str, bool)

    def convert(self, source: Any) -> Any:
        """
        Преобразование базовых примитивных типов данных.

        Args:
            source: Значение базового типа (число, строка, булево значение) или словарь примитивов

        Returns:
            Преобразованное базовое значение или словарь
        """
        if source is None:
            return None

        if isinstance(source, self.SUPPORTED_TYPES):
            return source

        if isinstance(source, dict):
            result = {}
            for key, value in source.items():
                if value is not None and not isinstance(value, self.SUPPORTED_TYPES):
                    raise argument_exception("source", f"Значение ключа '{key}' имеет неподдерживаемый тип {type(value).__name__}!")
                result[str(key)] = value
            return result

        raise argument_exception("source", f"Тип '{type(source).__name__}' не поддерживается базовым конвертером!")
