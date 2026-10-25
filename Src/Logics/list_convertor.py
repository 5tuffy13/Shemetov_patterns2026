from typing import Any, List, Optional
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import argument_exception


class list_convertor(abstract_convertor):
    """
    Конвертер коллекций (списков, кортежей, множеств)
    """

    def __init__(self, factory: Optional[Any] = None):
        self.__factory = factory

    @property
    def factory(self) -> Optional[Any]:
        return self.__factory

    @factory.setter
    def factory(self, value: Any) -> None:
        self.__factory = value

    def convert(self, source: Any) -> List[Any]:
        """
        Преобразование элементов коллекции в список сериализуемых данных.

        Args:
            source: Коллекция (list, tuple, set)

        Returns:
            Список сериализованных элементов
        """
        if source is None:
            return []

        if not isinstance(source, (list, tuple, set)):
            raise argument_exception(
                "source",
                f"Тип '{type(source).__name__}' не является поддерживаемой коллекцией!"
            )

        if self.__factory is None:
            return list(source)

        result = []
        for item in source:
            if item is None:
                result.append(None)
            else:
                conv = self.__factory.create_by_object(item)
                result.append(conv.convert(item))

        return result
