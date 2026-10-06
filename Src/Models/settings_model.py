from Src.Core.abstract_reference import abstract_reference
from Src.Models.organization_model import organization_model
from Src.Core.validator import validator


class settings_model(abstract_reference):
    """
    Модель настроек приложения
    """

    def __init__(self, name: str = "Настройки"):
        super().__init__(name)
        self.__company: organization_model | None = None
        self.__boss_name: str = ""
        self.__account_name: str = ""
        self.__is_first_start: bool = True

    @property
    def is_first_start(self) -> bool:
        """
        Флаг первого запуска системы
        """
        return self.__is_first_start

    @is_first_start.setter
    def is_first_start(self, value: bool) -> None:
        validator.validate_type(value, bool, field_name="is_first_start")
        self.__is_first_start = value

    @property
    def company(self) -> organization_model | None:
        """
        Карточка организации
        """
        return self.__company

    @company.setter
    def company(self, value: organization_model) -> None:
        validator.validate(value, organization_model, field_name="company")
        self.__company = value

    @property
    def organization(self) -> organization_model | None:
        """
        Алиас для карточки организации
        """
        return self.__company

    @organization.setter
    def organization(self, value: organization_model) -> None:
        self.company = value

    @property
    def boss_name(self) -> str:
        """
        Наименование директора
        """
        return self.__boss_name

    @boss_name.setter
    def boss_name(self, value: str) -> None:
        validator.validate(value, str, 255, field_name="boss_name")
        self.__boss_name = value.strip()

    @property
    def account_name(self) -> str:
        """
        Наименование главного бухгалтера
        """
        return self.__account_name

    @account_name.setter
    def account_name(self, value: str) -> None:
        validator.validate(value, str, 255, field_name="account_name")
        self.__account_name = value.strip()
