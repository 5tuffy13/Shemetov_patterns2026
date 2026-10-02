from Src.Core.abstract_reference import abstract_reference
from Src.Core.validator import validator


class range_model(abstract_reference):
    """
    Модель единицы измерения с поддержкой базовой единицы и коэффициента пересчета
    """

    def __init__(self, name: str = "", coeff: int | float = 1, base_range=None):
        """
        Инициализация единицы измерения
        """
        super().__init__(name)

        self.coeff = coeff

        if base_range is None:
            self.base_range = self
        else:
            self.base_range = base_range

    @property
    def base_range(self) -> "range_model":
        """
        Базовая единица измерения
        """
        return self.__base_range

    @base_range.setter
    def base_range(self, new_range: "range_model"):
        """
        Сеттер базовой единицы измерения
        """
        validator.validate_type(new_range, range_model, field_name="base_range")
        self.__base_range = new_range

    @property
    def coeff(self) -> int | float:
        """
        Коэффициент пересчета относительно базовой единицы
        """
        return self.__coeff

    @coeff.setter
    def coeff(self, new_coeff: int | float):
        """
        Сеттер коэффициента пересчета с валидацией типа и положительного значения
        """
        validator.validate_number(new_coeff, positive_only=True, field_name="coeff")
        self.__coeff = new_coeff
