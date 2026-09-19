from abc import ABC
import uuid
class abstract_reference(ABC):
    """
    Абстрактный класс-шаблон с полями id и name
    """
    def __init__(self, name: str):
        """
        Инициализация: присваивание имени и генерация id
        """

        self.__id = uuid.uuid4()
        self.name = name

    @property
    def name(self) -> str:
        """
        геттер для имени (названия)
        """
        return self.__name

    @property
    def id(self) -> str:
        """ 
        геттер для id
        """
        return str(self.__id)

    @name.setter
    def name(self, new_name: str):
        """
        сеттер названия с валидацией по типу данных и количеству символов
        """

        if not isinstance(new_name,str):
            raise TypeError("Ошибка: Имя должно иметь строковый тип данных")
        new_name = new_name.strip()
        if new_name == "":
            raise ValueError("Ошибка: Имя не должно быть пустым")
        if len(new_name) > 255:
            raise ValueError("Ошибка: Длина имени не должна превышать 255 символов")
        
        self.__name = new_name
        