from typing import Any, Optional
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

    def deserialize(self, source: Any, target_type: Optional[type] = None) -> Any:
        """
        Восстановление значения базового типа с опциональным приведением.
        """
        if source is None:
            return None

        if target_type is not None:
            try:
                if target_type is bool and isinstance(source, str):
                    return source.lower() in ("true", "1", "yes")
                return target_type(source)
            except Exception as ex:
                raise argument_exception(
                    "source",
                    f"Не удалось привести значение '{source}' к типу {target_type.__name__}: {ex}"
                )

        if isinstance(source, self.SUPPORTED_TYPES):
            return source

        raise argument_exception(
            "source",
            f"Неподдерживаемый тип данных для базовой десериализации: {type(source).__name__}"
        )
