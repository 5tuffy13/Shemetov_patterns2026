from typing import List, Optional, Set
from Src.Core.abstract_reference import abstract_reference
from Src.Core.exception import argument_exception, operation_exception
from Src.Core.validator import validator
from Src.Models.receipt_row_model import receipt_row_model


class receipt_model(abstract_reference):
    """
    Модель технологической карты (рецепта блюда или полуфабриката)
    """

    def __init__(
        self,
        name: str = "",
        portions: int = 1,
        cooking_time: int = 0,
        rows: Optional[List[receipt_row_model]] = None,
    ):
        """
        Инициализация технологической карты
        """
        super().__init__(name)

        self.__portions: int = 1
        self.__cooking_time: int = 0
        self.__rows: List[receipt_row_model] = []

        self.portions = portions
        self.cooking_time = cooking_time

        if rows is not None:
            validator.validate_type(rows, list, field_name="rows")
            for row in rows:
                self.add_row(row)

    @property
    def portions(self) -> int:
        """
        Количество порций
        """
        return self.__portions

    @portions.setter
    def portions(self, value: int):
        """
        Сеттер количества порций
        """
        validator.validate_type(value, int, field_name="portions")
        if value <= 0:
            raise argument_exception("portions", "Количество порций должно быть строго больше 0!")
        self.__portions = value

    @property
    def cooking_time(self) -> int:
        """
        Время приготовления блюда в минутах
        """
        return self.__cooking_time

    @cooking_time.setter
    def cooking_time(self, value: int):
        """
        Сеттер времени приготовления блюда в минутах
        """
        validator.validate_type(value, int, field_name="cooking_time")
        if value < 0:
            raise argument_exception("cooking_time", "Время приготовления не может быть отрицательным!")
        self.__cooking_time = value

    @property
    def rows(self) -> List[receipt_row_model]:
        """
        Состав строк технологической карты
        """
        return list(self.__rows)

    def add_row(self, row: receipt_row_model):
        """
        Добавление ингредиента или полуфабриката в технологическую карту
        """
        validator.validate_type(row, receipt_row_model, field_name="row")

        if row.nomenclature is not None:
            for existing in self.__rows:
                if existing.nomenclature is not None and existing.nomenclature == row.nomenclature:
                    raise argument_exception("row", f"Ингредиент '{row.nomenclature.name}' уже присутствует в рецепте!")

        if row.receipt is not None:
            if row.receipt == self:
                raise argument_exception("row", "Нельзя включить технологическую карту в саму себя!")
            for existing in self.__rows:
                if existing.receipt is not None and existing.receipt == row.receipt:
                    raise argument_exception("row", f"Технологическая карта '{row.receipt.name}' уже присутствует в рецепте!")

        self.__rows.append(row)

    def _calculate_total_weight(self, is_gross: bool, visited: Optional[Set[str]] = None) -> float:
        """
        Рекурсивное вычисление общей массы сырья с защитой от циклических зависимостей
        """
        if visited is None:
            visited = set()

        if self.id in visited:
            raise operation_exception(f"Обнаружена циклическая зависимость в технологической карте '{self.name}'!")

        visited.add(self.id)
        total = 0.0

        for row in self.__rows:
            if row.receipt is not None and isinstance(row.receipt, receipt_model):
                total += row.receipt._calculate_total_weight(is_gross=is_gross, visited=set(visited))
            else:
                total += row.gross if is_gross else row.net

        return total

    @property
    def gross(self) -> float:
        """
        Общая масса брутто сырья с рекурсивным учетом всех полуфабрикатов
        """
        return round(self._calculate_total_weight(is_gross=True), 4)

    @property
    def gross_weight(self) -> float:
        """
        Общая масса брутто сырья
        """
        return self.gross

    @property
    def net(self) -> float:
        """
        Общая масса нетто с рекурсивным учетом всех полуфабрикатов
        """
        return round(self._calculate_total_weight(is_gross=False), 4)

    @property
    def net_weight(self) -> float:
        """
        Общая масса нетто
        """
        return self.net
