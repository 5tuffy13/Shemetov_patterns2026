from Src.Core.abstract_reference import abstract_reference
from Src.Core.validator import validator


class storage_model(abstract_reference):
    """
    Модель склада для учета мест хранения сырья, заготовок и продукции
    """

    def __init__(self, name: str = "", address: str = ""):
        """
        Инициализация склада с наименованием и адресом
        """
        super().__init__(name)
        if address:
            self.address = address

    @property
    def address(self) -> str:
        """
        Адрес склада
        """
        return getattr(self, "_storage_model__address", "")

    @address.setter
    def address(self, value: str):
        """
        Сеттер адреса склада
        """
        validator.validate(value, str, field_name="address")
        self.__address = value.strip()
