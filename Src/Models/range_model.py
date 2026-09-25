from Src.Core.abstract_reference import abstract_reference
from Src.Core.exception import argument_exception


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
        if not isinstance(new_range, range_model):
            raise argument_exception("base_range", "Ошибка: Неверный тип переменной!")
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
        if not isinstance(new_coeff, (int, float)):
            raise argument_exception("coeff", "Ошибка: Коэффициент должен иметь числовой тип данных!")
        if new_coeff <= 0:
            raise argument_exception("coeff", "Ошибка: Коэффициент не может быть меньше или равен нулю!")
        self.__coeff = new_coeff
