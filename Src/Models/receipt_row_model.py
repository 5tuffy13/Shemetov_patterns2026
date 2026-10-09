from typing import Optional
from Src.Core.abstract_reference import abstract_reference
from Src.Core.exception import argument_exception
from Src.Core.validator import validator
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class receipt_row_model(abstract_reference):
    """
    Модель строки ингредиента или полуфабриката технологической карты
    """

    def __init__(
        self,
        nomenclature: Optional[nomenclature_model] = None,
        gross: int | float = 0,
        net: int | float = 0,
        range: Optional[range_model] = None,
        receipt: Optional[abstract_reference] = None,
    ):
        """
        Инициализация строки технологической карты
        """
        super().__init__()

        self.__nomenclature: Optional[nomenclature_model] = None
        self.__receipt: Optional[abstract_reference] = None
        self.__range: Optional[range_model] = None
        self.__gross: float = 0.0
        self.__net: float = 0.0

        if nomenclature is not None:
            self.nomenclature = nomenclature
        if receipt is not None:
            self.receipt = receipt
        if range is not None:
            self.range = range
        if gross > 0:
            self.gross = gross
        if net > 0:
            self.net = net

    @property
    def nomenclature(self) -> Optional[nomenclature_model]:
        """
        Ингредиент рецепта
        """
        return self.__nomenclature

    @nomenclature.setter
    def nomenclature(self, value: nomenclature_model):
        """
        Сеттер ингредиента с валидацией типа
        """
        validator.validate_type(value, nomenclature_model, field_name="nomenclature")
        self.__nomenclature = value
        self.name = value.name
        if self.__range is None and value.range is not None:
            self.__range = value.range

    @property
    def receipt(self) -> Optional[abstract_reference]:
        """
        Вложенная технологическая карта полуфабриката
        """
        return self.__receipt

    @receipt.setter
    def receipt(self, value: abstract_reference):
        """
        Сеттер вложенной технологической карты
        """
        validator.validate_type(value, abstract_reference, field_name="receipt")
        self.__receipt = value
        if hasattr(value, "name") and value.name:
            self.name = value.name

    @property
    def range(self) -> Optional[range_model]:
        """
        Единица измерения расхода ингредиента
        """
        return self.__range

    @range.setter
    def range(self, value: range_model):
        """
        Сеттер единицы измерения с валидацией типа
        """
        validator.validate_type(value, range_model, field_name="range")
        self.__range = value

    @property
    def gross(self) -> float:
        """
        Масса брутто ингредиента или вложенного полуфабриката
        """
        if self.__receipt is not None and hasattr(self.__receipt, "gross"):
            return float(self.__receipt.gross)
        return self.__gross

    @gross.setter
    def gross(self, value: int | float):
        """
        Сеттер массы брутто
        """
        validator.validate_number(value, positive_only=True, field_name="gross")
        val = float(value)
        if self.__net > 0 and val < self.__net:
            raise argument_exception("gross", "Масса брутто не может быть меньше массы нетто!")
        self.__gross = val

    @property
    def gross_weight(self) -> float:
        """
        Масса брутто
        """
        return self.gross

    @gross_weight.setter
    def gross_weight(self, value: int | float):
        """
        Сеттер массы брутто
        """
        self.gross = value

    @property
    def net(self) -> float:
        """
        Масса нетто ингредиента или вложенного полуфабриката
        """
        if self.__receipt is not None and hasattr(self.__receipt, "net"):
            return float(self.__receipt.net)
        return self.__net

    @net.setter
    def net(self, value: int | float):
        """
        Сеттер массы нетто
        """
        validator.validate_number(value, positive_only=True, field_name="net")
        val = float(value)
        if self.__gross > 0 and val > self.__gross:
            raise argument_exception("net", "Масса нетто не может превышать массу брутто!")
        self.__net = val

    @property
    def net_weight(self) -> float:
        """
        Масса нетто
        """
        return self.net

    @net_weight.setter
    def net_weight(self, value: int | float):
        """
        Сеттер массы нетто
        """
        self.net = value

    def set_weights(self, gross: int | float, net: int | float):
        """
        Одновременная установка значений массы брутто и нетто
        """
        self.gross = gross
        self.net = net
