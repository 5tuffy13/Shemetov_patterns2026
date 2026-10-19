from Src.Core.abstract_reference import abstract_reference
from Src.Core.validator import validator


class entity_description_header_dto(abstract_reference):
    """
    DTO элемента описания заголовка доменной сущности
    """

    def __init__(self, field: str = "", value: str = ""):
        super().__init__(name=field if field else "header_field")
        self.__field: str = ""
        self.__value: str = ""

        if field:
            self.field = field
        if value:
            self.value = value

    @property
    def field(self) -> str:
        """
        Наименование поля сущности
        """
        return self.__field

    @field.setter
    def field(self, value: str) -> None:
        validator.validate_type(value, str, field_name="field")
        self.__field = value.strip()

    @property
    def value(self) -> str:
        """
        Строковое значение поля сущности
        """
        return self.__value

    @value.setter
    def value(self, value: str) -> None:
        validator.validate_type(value, str, field_name="value")
        self.__value = value.strip()
