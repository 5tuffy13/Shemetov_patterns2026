from Src.Core.abstract_model import abstact_model


class entity_model(abstact_model):
    """
    Базовая сущность с наименованием (совместимость с Patterns2026)
    """

    def __init__(self, name: str = ""):
        super().__init__(name)
