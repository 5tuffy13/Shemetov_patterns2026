from Src.Core.abstract_reference import abstract_reference
from Src.Core.validator import validator
from Src.Models.range_model import range_model
from Src.Models.nomenclature_group_model import nomenclature_group_model


class nomenclature_model(abstract_reference):
    """
    Модель номенклатуры (товара, сырья, полуфабриката или готовой продукции)
    """

    def __init__(
        self,
        name: str = "",
        full_name: str = "",
        group: nomenclature_group_model = None,
        range: range_model = None,
    ):
        """
        Инициализация номенклатуры
        """
        super().__init__(name)

        self.full_name = full_name
        self.group = group
        self.range = range

    @property
    def full_name(self) -> str:
        """
        Полное наименование номенклатуры
        """
        return self.__full_name

    @full_name.setter
    def full_name(self, new_name: str):
        """
        Сеттер полного наименования с ограничением до 255 символов
        """
        validator.validate(new_name, str, 255, field_name="full_name")
        self.__full_name = new_name.strip()

    @property
    def group(self) -> nomenclature_group_model:
        """
        Группа номенклатуры
        """
        return self.__group

    @group.setter
    def group(self, new_group: nomenclature_group_model):
        """
        Сеттер группы номенклатуры
        """
        validator.validate(new_group, nomenclature_group_model, field_name="group")
        self.__group = new_group

    @property
    def range(self) -> range_model:
        """
        Единица измерения номенклатуры
        """
        return self.__range

    @range.setter
    def range(self, new_range: range_model):
        """
        Сеттер единицы измерения номенклатуры
        """
        validator.validate(new_range, range_model, field_name="range")
        self.__range = new_range
