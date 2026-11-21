import datetime
from typing import Optional
from Src.Core.abstract_reference import abstract_reference
from Src.Core.validator import argument_exception, validator
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model


class transaction_model(abstract_reference):
    """
    Доменная модель складской транзакции (движения номенклатуры)
    """

    def __init__(
        self,
        name: str = "Складская транзакция",
        storage: Optional[storage_model] = None,
        nomenclature: Optional[nomenclature_model] = None,
        range_item: Optional[range_model] = None,
        value: float = 1.0,
        period: Optional[datetime.datetime] = None,
    ):
        """
        Инициализация складской проводки
        """
        super().__init__(name)
        self.__storage: Optional[storage_model] = None
        self.__nomenclature: Optional[nomenclature_model] = None
        self.__range: Optional[range_model] = None
        self.__value: float = 1.0
        self.__period: datetime.datetime = datetime.datetime.now()

        if storage is not None:
            self.storage = storage
        if nomenclature is not None:
            self.nomenclature = nomenclature
        if range_item is not None:
            self.range = range_item
        self.value = value
        if period is not None:
            self.period = period

    @property
    def storage(self) -> Optional[storage_model]:
        """
        Склад проведения операции
        """
        return self.__storage

    @storage.setter
    def storage(self, val: storage_model):
        """
        Сеттер склада с валидацией типа
        """
        validator.validate(val, storage_model, field_name="storage")
        self.__storage = val

    @property
    def nomenclature(self) -> Optional[nomenclature_model]:
        """
        Номенклатура операции
        """
        return self.__nomenclature

    @nomenclature.setter
    def nomenclature(self, val: nomenclature_model):
        """
        Сеттер номенклатуры с валидацией типа
        """
        validator.validate(val, nomenclature_model, field_name="nomenclature")
        self.__nomenclature = val

    @property
    def range(self) -> Optional[range_model]:
        """
        Единица измерения операции
        """
        return self.__range

    @range.setter
    def range(self, val: range_model):
        """
        Сеттер единицы измерения с валидацией типа
        """
        validator.validate(val, range_model, field_name="range")
        self.__range = val

    @property
    def value(self) -> float:
        """
        Объем транзакции (+ приход, - расход)
        """
        return self.__value

    @value.setter
    def value(self, val: float):
        """
        Сеттер объема с запретом нулевого значения
        """
        validator.validate(val, (int, float), field_name="value")
        num_val = float(val)
        if num_val == 0.0:
            raise argument_exception("value", "Значение транзакции не может быть равным 0!")
        self.__value = num_val

    @property
    def period(self) -> datetime.datetime:
        """
        Дата и время проведения транзакции
        """
        return self.__period

    @period.setter
    def period(self, val: datetime.datetime):
        """
        Сеттер даты и времени транзакции
        """
        validator.validate(val, datetime.datetime, field_name="period")
        self.__period = val
