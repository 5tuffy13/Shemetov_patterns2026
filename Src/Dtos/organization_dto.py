from Src.Core.abstract_dto import abstract_dto
from Src.Core.validator import validator
from Src.Models.organization_model import organization_model


class organization_dto(abstract_dto):
    """
    Структура передачи данных для организации
    """

    def __init__(self):
        self.__id: str = ""
        self.__name: str = ""
        self.__inn: str = ""
        self.__bik: str = ""
        self.__account: str = ""
        self.__ownership_form: str = ""

    @property
    def id(self) -> str:
        return self.__id

    @id.setter
    def id(self, value: str) -> None:
        validator.validate_type(value, str, field_name="id")
        self.__id = value.strip()

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        validator.validate_type(value, str, field_name="name")
        self.__name = value.strip()

    @property
    def inn(self) -> str:
        return self.__inn

    @inn.setter
    def inn(self, value: str) -> None:
        validator.validate_type(value, str, field_name="inn")
        self.__inn = value.strip()

    @property
    def bik(self) -> str:
        return self.__bik

    @bik.setter
    def bik(self, value: str) -> None:
        validator.validate_type(value, str, field_name="bik")
        self.__bik = value.strip()

    @property
    def account(self) -> str:
        return self.__account

    @account.setter
    def account(self, value: str) -> None:
        validator.validate_type(value, str, field_name="account")
        self.__account = value.strip()

    @property
    def ownership_form(self) -> str:
        return self.__ownership_form

    @ownership_form.setter
    def ownership_form(self, value: str) -> None:
        validator.validate_type(value, str, field_name="ownership_form")
        self.__ownership_form = value.strip()

    def from_domain_model(self, source: organization_model) -> "organization_dto":
        """
        Создать DTO из доменной модели организации
        """
        validator.validate_type(source, organization_model, field_name="source")

        dto = organization_dto()
        dto.id = source.id
        dto.name = source.name
        dto.inn = source.inn
        dto.bik = source.bik
        dto.account = source.account
        dto.ownership_form = source.ownership_form
        return dto
