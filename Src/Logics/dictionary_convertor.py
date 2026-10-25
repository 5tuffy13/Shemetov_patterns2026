from typing import Any, Dict, Optional
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import argument_exception


class dictionary_convertor(abstract_convertor):
    """
    Конвертер словарей
    """

    def __init__(self, factory: Optional[Any] = None):
        self.__factory = factory

    @property
    def factory(self) -> Optional[Any]:
        return self.__factory

    @factory.setter
    def factory(self, value: Any) -> None:
        self.__factory = value

    def convert(self, source: Any) -> Dict[str, Any]:
        """
        Преобразование словаря в сериализуемый словарь со строковыми ключами.

        Args:
            source: Исходный словарь

        Returns:
            Сериализованный словарь
        """
        if source is None:
            return {}

        if not isinstance(source, dict):
            raise argument_exception(
                "source",
                f"Тип '{type(source).__name__}' не является словарем!"
            )

        result = {}
        for key, value in source.items():
            str_key = str(key)
            if value is None:
                result[str_key] = None
            elif self.__factory is not None:
                conv = self.__factory.create_by_object(value)
                result[str_key] = conv.convert(value)
            else:
                result[str_key] = value

        return result
