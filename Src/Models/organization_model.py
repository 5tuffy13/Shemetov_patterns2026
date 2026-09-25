from Src.Core.abstract_reference import abstract_reference
from Src.Core.exception import argument_exception


class organization_model(abstract_reference):
    """
    Модель организации (юридического лица)
    """

    def __init__(self, name: str = "", inn: str = "", bik: str = "", account: str = "", ownership_form: str = ""):
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

    @property
    def bik(self) -> str:
        """
        БИК банка организации (9 цифр)
        """
        return self.__bik

    @property
    def account(self) -> str:
        """
        Банковский счет организации (11 цифр)
        """
        return self.__account

    @property
    def ownership_form(self) -> str:
        """
        Форма собственности организации
        """
        return self.__ownership_form

    @inn.setter
    def inn(self, new_inn: str):
        """
        Сеттер ИНН с валидацией длины (10 или 12 символов) и содержания только цифр
        """
        if not isinstance(new_inn, str):
            raise argument_exception("inn", "Неверный тип данных!")
        new_inn = new_inn.strip()

        if not new_inn.isdigit():
            raise argument_exception("inn", "Значение может состоять только из цифр!")
        if not (len(new_inn) == 10 or len(new_inn) == 12):
            raise argument_exception("inn", "ИНН может быть длиной 10 или 12 символов!")

        self.__inn = new_inn

    @bik.setter
    def bik(self, new_bik: str):
        """
        Сеттер БИК с валидацией длины (9 цифр)
        """
        if not isinstance(new_bik, str):
            raise argument_exception("bik", "Неверный тип данных!")
        new_bik = new_bik.strip()
        if not new_bik.isdigit():
            raise argument_exception("bik", "БИК должен состоять только из цифр!")
        if len(new_bik) != 9:
            raise argument_exception("bik", "БИК должен содержать ровно 9 цифр!")
        self.__bik = new_bik

    @account.setter
    def account(self, new_account: str):
        """
        Сеттер банковского счета с валидацией длины (11 цифр)
        """
        if not isinstance(new_account, str):
            raise argument_exception("account", "Неверный тип данных!")
        new_account = new_account.strip()
        if not new_account.isdigit():
            raise argument_exception("account", "Счет должен состоять только из цифр!")
        if len(new_account) != 11:
            raise argument_exception("account", "Счет должен содержать 11 цифр!")
        self.__account = new_account

    @ownership_form.setter
    def ownership_form(self, new_form: str):
        """
        Сеттер формы собственности с ограничением длины до 5 символов
        """
        if not isinstance(new_form, str):
            raise argument_exception("ownership_form", "Неверный тип данных!")
        new_form = new_form.strip()
        if new_form == "":
            raise argument_exception("ownership_form", "Форма собственности не может быть пустой!")
        if len(new_form) > 5:
            raise argument_exception("ownership_form", "Форма собственности не должна превышать 5 символов!")
        self.__ownership_form = new_form
