from typing import List
from Src.Core.abstract_reference import abstract_reference
from Src.Core.validator import validator


class entity_description_table_dto(abstract_reference):
    """
    DTO строки табличной части доменной сущности (агрегата)
    """

    def __init__(self, columns: List[str] = None, values: List[str] = None):
        super().__init__(name="table_row")
        self.__columns: List[str] = []
        self.__values: List[str] = []

        if columns is not None:
            self.columns = columns
        if values is not None:
            self.values = values

    @property
    def columns(self) -> List[str]:
        """
        Список наименований колонок
        """
        return self.__columns

    @columns.setter
    def columns(self, value: List[str]) -> None:
        validator.validate_type(value, list, field_name="columns")
        for item in value:
            validator.validate_type(item, str, field_name="column_item")
        self.__columns = value

    @property
    def values(self) -> List[str]:
        """
        Список строковых значений строки
        """
        return self.__values

    @values.setter
    def values(self, value: List[str]) -> None:
        validator.validate_type(value, list, field_name="values")
        for item in value:
            validator.validate_type(item, str, field_name="value_item")
        self.__values = value
