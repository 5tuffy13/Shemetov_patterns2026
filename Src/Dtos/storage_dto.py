from Src.Core.abstract_dto import abstract_dto
from Src.Core.validator import validator
from Src.Models.storage_model import storage_model


class storage_dto(abstract_dto):
    """
    Структура передачи данных для склада
    """

    def __init__(self):
        self.__id: str = ""
        self.__name: str = ""
        self.__address: str = ""

    @property
    def id(self) -> str:
        """
        Идентификатор
        """
        return self.__id

    @id.setter
    def id(self, value: str) -> None:
        validator.validate_type(value, str, field_name="id")
        self.__id = value.strip()

    @property
    def name(self) -> str:
        """
        Наименование склада
        """
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        validator.validate_type(value, str, field_name="name")
        self.__name = value.strip()

    @property
    def address(self) -> str:
        """
        Адрес склада
        """
        return self.__address

    @address.setter
    def address(self, value: str) -> None:
        validator.validate_type(value, str, field_name="address")
        self.__address = value.strip()

    def from_domain_model(self, source: storage_model) -> "storage_dto":
        """
        Создать DTO из доменной модели склада
        """
        validator.validate_type(source, storage_model, field_name="source")

        dto = storage_dto()
        dto.id = source.id
        dto.name = source.name
        dto.address = source.address
        return dto
