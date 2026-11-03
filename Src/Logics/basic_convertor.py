from typing import Any
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import argument_exception


class basic_convertor(abstract_convertor):
    """
    Конвертер базовых примитивных типов данных (числовые, строковые, логические)
    """

    SUPPORTED_TYPES = (int, float, str, bool)

    def convert(self, source: Any) -> Any:
        """
        Преобразование базовых примитивных типов данных.

        Args:
            source: Значение базового типа (число, строка, булево значение)

        Returns:
            Исходное базовое значение
        """
        if source is None:
            return None

        if isinstance(source, self.SUPPORTED_TYPES):
            return source

        raise argument_exception(
            "source",
            f"Тип '{type(source).__name__}' не поддерживается базовым конвертером!"
        )
