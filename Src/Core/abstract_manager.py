from abc import ABC
from typing import Any


class abstract_manager(ABC):
    """
    Абстрактный класс для реализации менеджеров загрузки и обработки данных
    """

    def __init__(self):
        # Полный путь к файлу
        self._file_name: str = ""
        # Флаг: загрузка и обработка завершена успешно
        self._is_loaded: bool = False
        # Загруженные сырые данные
        self._data: Any = None

    def load(self, file_name: str = "") -> None:
        """
        Загрузить данные из источника
        """
        pass

    def convert(self) -> bool:
        """
        Обработать и сконвертировать загруженные данные
        """
        return False

    @property
    def is_loaded(self) -> bool:
        """
        Флаг: данные подготовлены
        """
        return self._is_loaded

    @is_loaded.setter
    def is_loaded(self, value: bool) -> None:
        """
        Сеттер флага загрузки
        """
        self._is_loaded = bool(value)
