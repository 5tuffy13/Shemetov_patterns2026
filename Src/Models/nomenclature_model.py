from Src.Core.abstract_reference import abstract_reference
from Src.Core.exception import argument_exception
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
        if not isinstance(new_name, str):
            raise argument_exception("full_name", "Ошибка: Имя должно иметь строковый тип данных!")
        new_name = new_name.strip()
        if new_name == "":
            raise argument_exception("full_name", "Ошибка: Некорректно передан параметр!")
        if len(new_name) > 255:
            raise argument_exception("full_name", "Ошибка: Длина имени не должна превышать 255 символов!")

        self.__full_name = new_name

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
        if not isinstance(new_group, nomenclature_group_model):
            raise argument_exception("group", "Ошибка: Неверный тип аргумента!")

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
        if not isinstance(new_range, range_model):
            raise argument_exception("range", "Ошибка: Неверный тип аргумента!")
        self.__range = new_range
