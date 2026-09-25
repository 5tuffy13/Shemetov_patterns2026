from Src.Core.abstract_reference import abstract_reference


class nomenclature_group_model(abstract_reference):
    """
    Модель группы номенклатуры
    """

    def __init__(self, name: str = ""):
        """
        Инициализация группы номенклатуры с наименованием
        """
        super().__init__(name)
