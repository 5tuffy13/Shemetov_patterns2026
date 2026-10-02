from Src.Core.abstract_reference import abstract_reference


class abstact_model(abstract_reference):
    """
    Базовый класс моделей с генерацией уникального кода (совместимость с Patterns2026)
    """

    def __init__(self, name: str = ""):
        super().__init__(name)

    @property
    def unique_code(self) -> str:
        """
        Уникальный код сущности
        """
        return self.id

    @unique_code.setter
    def unique_code(self, value: str):
        self.id = value
