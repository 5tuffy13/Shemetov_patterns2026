from Src.Core.abstract_reference import abstract_reference
from Src.Core.validator import validator


class organization_model(abstract_reference):
    """
    Модель организации (юридического лица)
    """

    def __init__(
        self,
        name: str = "",
        inn: str = "",
        bik: str = "",
        account: str = "",
        ownership_form: str = "",
    ):
        """
        Инициализация организации
        """
        super().__init__(name)
        self.inn = inn
        self.bik = bik
        self.account = account
        self.ownership_form = ownership_form

    @property
    def inn(self) -> str:
        """
        ИНН организации (10 или 12 цифр)
        """
        return self.__inn

    @inn.setter
    def inn(self, new_inn: str):
        """
        Сеттер ИНН с валидацией длины (10 или 12 символов) и содержания только цифр
        """
        validator.validate_digits(new_inn, allowed_lengths=(10, 12), allow_int=False, field_name="inn")
        self.__inn = new_inn.strip()

    @property
    def bik(self) -> str:
        """
        БИК банка организации (9 цифр)
        """
        return self.__bik

    @bik.setter
    def bik(self, new_bik: str):
        """
        Сеттер БИК с валидацией длины (9 цифр)
        """
        validator.validate_digits(new_bik, length=9, allow_int=False, field_name="bik")
        self.__bik = new_bik.strip()

    @property
    def account(self) -> str:
        """
        Банковский счет организации (11 цифр)
        """
        return self.__account

    @account.setter
    def account(self, new_account: str):
        """
        Сеттер банковского счета с валидацией длины (11 цифр)
        """
        validator.validate_digits(new_account, length=11, allow_int=False, field_name="account")
        self.__account = new_account.strip()

    @property
    def ownership_form(self) -> str:
        """
        Форма собственности организации
        """
        return self.__ownership_form

    @ownership_form.setter
    def ownership_form(self, new_form: str):
        """
        Сеттер формы собственности с ограничением длины до 5 символов
        """
        validator.validate(new_form, str, 5, field_name="ownership_form")
        self.__ownership_form = new_form.strip()
