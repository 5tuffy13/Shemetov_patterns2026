from abc import ABC
import uuid
from Src.Core.exception import argument_exception
from Src.Core.validator import validator


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
        validator.validate(new_name, str, 50, field_name="name")
        self.__name = new_name.strip()

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
        validator.validate(new_id, str, field_name="id")
        self.__id = new_id.strip()

    def __eq__(self, value) -> bool:
        """
        Сравнение двух сущностей по их id
        """
        if not isinstance(value, abstract_reference):
            return False
        return self.id == value.id
