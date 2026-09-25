from Src.Core.abstract_reference import abstract_reference


class storage_model(abstract_reference):
    """
    Модель склада для учета мест хранения сырья, заготовок и продукции
    """

    def __init__(self, name: str = ""):
        """
        Инициализация склада с наименованием
        """
        super().__init__(name)
