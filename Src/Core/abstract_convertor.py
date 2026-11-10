from abc import ABC, abstractmethod
from typing import Any, Optional
from Src.Core.validator import validator


class abstract_convertor(ABC):
    """
    Абстрактный класс конвертера данных для сериализации и десериализации
    """

    def __init__(self):
        self.__error_text: str = ""

    @abstractmethod
    def convert(self, source: Any) -> Any:
        """
        Преобразование переданного объекта в сериализуемое представление
        """
        pass

    def serialize(self, field: str, object: Any) -> dict:
        """
        Сериализовать объект под указанным именем поля
        """
        validator.validate_type(field, str, field_name="field")
        try:
            return {field: self.convert(object)}
        except Exception as ex:
            self.set_exception(ex)
            return {field: None}

    def deserialize(self, source: Any, target_type: Optional[type] = None) -> Any:
        """
        Десериализовать представление данных в целевой объект
        """
        pass

    @property
    def error_text(self) -> str:
        """
        Текст ошибки конвертации
        """
        return self.__error_text

    @error_text.setter
    def error_text(self, value: str) -> None:
        validator.validate_type(value, str, field_name="error_text")
        self.__error_text = value.strip()

    def set_exception(self, ex: Exception) -> None:
        """
        Установить текст ошибки из перехваченного исключения
        """
        self.__error_text = f"Ошибка конвертации: {ex}"
