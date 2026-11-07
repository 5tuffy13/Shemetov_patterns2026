from typing import Any, Dict, List, Optional
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import argument_exception


class list_convertor(abstract_convertor):
    """
    Конвертер коллекций (списков, кортежей, множеств)
    """

    def __init__(self, factory: Optional[abstract_convert_factory] = None):
        super().__init__()
        self.__factory = factory

    @property
    def factory(self) -> Optional[abstract_convert_factory]:
        return self.__factory

    @factory.setter
    def factory(self, value: abstract_convert_factory) -> None:
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
                convertor = self.__factory.create(type(item))
                result.append(convertor.convert(item))

        return result

    def deserialize(
        self,
        source: Any,
        target_type: Optional[type] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        """
        Десериализация списка элементов в исходные объекты
        """
        if source is None:
            return []

        if not isinstance(source, (list, tuple)):
            raise argument_exception(
                "source",
                f"Тип '{type(source).__name__}' не является списком для десериализации!"
            )

        result = []
        for item in source:
            if item is None:
                result.append(None)
            elif target_type is not None and self.__factory is not None:
                conv = self.__factory.create(target_type)
                if hasattr(conv, "deserialize"):
                    result.append(conv.deserialize(item, target_type=target_type, context=context))
                else:
                    result.append(item)
            elif isinstance(item, dict) and self.__factory is not None:
                domain_conv = getattr(self.__factory, "domain_convertor", None)
                if domain_conv is not None:
                    result.append(domain_conv.deserialize(item, target_type=target_type, context=context))
                else:
                    result.append(item)
            else:
                result.append(item)

        return result
