from typing import Any, Dict, Optional
from Src.Core.abstract_dto import abstract_dto
from Src.Core.validator import validator
from Src.Dtos.organization_dto import organization_dto
from Src.Models.settings_model import settings_model


class settings_dto(abstract_dto):
    """
    Структура передачи данных для настроек приложения
    """

    def __init__(self):
        self.__id: str = ""
        self.__name: str = "Настройки"
        self.__company: Optional[organization_dto] = None
        self.__boss_name: str = ""
        self.__account_name: str = ""
        self.__is_first_start: bool = True
        self.__response_format: str = "Markdown"

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
    def company(self) -> Optional[organization_dto]:
        return self.__company

    @company.setter
    def company(self, value: Any) -> None:
        if value is None:
            self.__company = None
        elif isinstance(value, organization_dto):
            self.__company = value
        elif isinstance(value, dict):
            self.__company = organization_dto().from_dict(value)

    @property
    def boss_name(self) -> str:
        return self.__boss_name

    @boss_name.setter
    def boss_name(self, value: str) -> None:
        validator.validate_type(value, str, field_name="boss_name")
        self.__boss_name = value.strip()

    @property
    def account_name(self) -> str:
        return self.__account_name

    @account_name.setter
    def account_name(self, value: str) -> None:
        validator.validate_type(value, str, field_name="account_name")
        self.__account_name = value.strip()

    @property
    def is_first_start(self) -> bool:
        return self.__is_first_start

    @is_first_start.setter
    def is_first_start(self, value: bool) -> None:
        validator.validate_type(value, bool, field_name="is_first_start")
        self.__is_first_start = value

    @property
    def response_format(self) -> str:
        return self.__response_format

    @response_format.setter
    def response_format(self, value: str) -> None:
        validator.validate_type(value, str, field_name="response_format")
        self.__response_format = value.strip()

    def from_domain_model(self, source: settings_model) -> "settings_dto":
        """
        Создать DTO из доменной модели настроек
        """
        validator.validate_type(source, settings_model, field_name="source")

        dto = settings_dto()
        dto.id = source.id
        dto.name = source.name
        dto.boss_name = source.boss_name
        dto.account_name = source.account_name
        dto.is_first_start = source.first_start

        if source.response_format is not None:
            dto.response_format = getattr(source.response_format, "name", str(source.response_format))

        if source.company is not None:
            dto.company = organization_dto().from_domain_model(source.company)

        return dto

    def from_dict(self, data: Dict[str, Any]) -> "settings_dto":
        """
        Заполнить поля DTO из словаря
        """
        validator.validate_type(data, dict, field_name="data")

        if "id" in data and data["id"] is not None:
            self.id = str(data["id"])
        if "name" in data and data["name"] is not None:
            self.name = str(data["name"])

        company_raw = data.get("company") or data.get("organization")
        if company_raw and isinstance(company_raw, dict):
            self.company = organization_dto().from_dict(company_raw)

        if "boss_name" in data and data["boss_name"] is not None:
            self.boss_name = str(data["boss_name"])
        if "account_name" in data and data["account_name"] is not None:
            self.account_name = str(data["account_name"])

        flag = data.get("first_start", data.get("is_first_start"))
        if flag is not None:
            self.is_first_start = bool(flag)

        fmt = data.get("response_format")
        if fmt is not None:
            self.response_format = str(fmt)

        return self
