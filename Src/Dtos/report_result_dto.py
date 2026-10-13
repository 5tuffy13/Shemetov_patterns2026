from typing import List, Union
from Src.Core.abstract_reference import abstract_reference
from Src.Core.validator import validator


class report_result_dto(abstract_reference):
    """
    Модель передачи данных (DTO) для хранения результата формирования отчета
    """

    def __init__(self, text: str = "", binary: Union[List[int], bytes, None] = None):
        """
        Инициализация DTO результата отчета
        """
        super().__init__()
        self.__text: str = ""
        self.__binary: list = []

        if text:
            self.text = text
        if binary is not None:
            self.binary = binary

    @property
    def text(self) -> str:
        """
        Текстовое представление отчета
        """
        return self.__text

    @text.setter
    def text(self, value: str):
        """
        Сеттер текстового представления отчета
        """
        validator.validate_type(value, str, field_name="text")
        self.__text = value
        self.__binary = []

    @property
    def binary(self) -> list:
        """
        Бинарное представление отчета
        """
        return self.__binary

    @binary.setter
    def binary(self, value: Union[list, bytes]):
        """
        Сеттер бинарного представления отчета
        """
        if isinstance(value, bytes):
            value = list(value)
        validator.validate_type(value, list, field_name="binary")
        if len(value) > 0:
            self.__text = ""
            self.__binary = value
