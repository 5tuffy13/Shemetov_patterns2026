from abc import ABC
import uuid
from Src.Core.exception import argument_exception


class abstract_reference(ABC):
    """
    Абстрактный класс-шаблон с полями id и name
    """

    def __init__(self, name: str = None):
        """
        Инициализация: генерация id и опциональная установка наименования
        """
        self.__id = uuid.uuid4()
        if name is not None:
            self.name = name

    @property
    def name(self) -> str:
        """
        Геттер для имени (названия)
        """
        try:
            return self.__name
        except AttributeError:
            raise argument_exception("name", "Ошибка: Имя не задано!")

    @name.setter
    def name(self, new_name: str):
        """
        Сеттер названия с валидацией по типу данных и количеству символов (до 50)
        """
        if not isinstance(new_name, str):
            raise argument_exception("name", "Ошибка: Имя должно иметь строковый тип данных!")
        new_name = new_name.strip()
        if new_name == "":
            raise argument_exception("name", "Некорректно передан параметр!")
        if len(new_name) > 50:
            raise argument_exception("name", "Ошибка: Длина имени не должна превышать 50 символов!")

        self.__name = new_name

    @property
    def id(self) -> str:
        """
        Геттер для id
        """
        return str(self.__id)

    @id.setter
    def id(self, new_id: str):
        """
        Сеттер id с проверкой строкового типа и непустой строки
        """
        if not isinstance(new_id, str):
            raise argument_exception("id", "Ошибка: id должен иметь строковый тип данных!")
        if new_id.strip() == "":
            raise argument_exception("id", "Некорректно передан параметр")
        self.__id = new_id

    def __eq__(self, value) -> bool:
        """
        Сравнение двух сущностей по их id
        """
        if not isinstance(value, abstract_reference):
            return False
        return self.id == value.id
