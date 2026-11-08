from typing import Any, Dict, List, Optional
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_mapping_factory import abstract_mapping_factory
from Src.Core.exception import argument_exception
from Src.Core.validator import validator


class list_convertor(abstract_convertor):
    """
    Конвертер коллекций (списков, кортежей, множеств)
    """

    def __init__(
        self,
        convert_factory: Optional[abstract_convert_factory] = None,
        mapping_factory: Optional[abstract_mapping_factory] = None,
        factory: Optional[abstract_convert_factory] = None,
    ):
        super().__init__()
        self.__convert_factory = convert_factory if convert_factory is not None else factory
        self.__mapping_factory = mapping_factory

    @property
    def factory(self) -> Optional[abstract_convert_factory]:
        return self.__convert_factory

    @factory.setter
    def factory(self, value: abstract_convert_factory) -> None:
        self.__convert_factory = value

    @property
    def mapping_factory(self) -> Optional[abstract_mapping_factory]:
        return self.__mapping_factory

    @mapping_factory.setter
    def mapping_factory(self, value: abstract_mapping_factory) -> None:
        self.__mapping_factory = value

    def convert(self, source: Any) -> List[Any]:
        """
        Преобразование элементов коллекции в список сериализуемых данных
        """
        if source is None:
            return []

        if not isinstance(source, (list, tuple, set)):
            raise argument_exception(
                "source",
                f"Тип '{type(source).__name__}' не является поддерживаемой коллекцией!"
            )

        if self.__convert_factory is None:
            return list(source)

        result = []
        for item in source:
            if item is None:
                result.append(None)
            else:
                convertor = self.__convert_factory.create(type(item))
                result.append(convertor.convert(item))

        return result

    def serialize(self, field: str, items: Any) -> dict:
        """
        Сериализация коллекции под указанным именем поля
        """
        validator.validate_type(field, str, field_name="field")
        return {field: self.convert(items)}

    def deserialize(
        self,
        source: Any,
        target_type: Optional[type] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        """
        Полиморфная десериализация списка элементов в доменные модели
        """
        if source is None:
            return []

        # Если передан словарь вида {field: [...]}, извлекаем список
        raw_items = source
        if isinstance(source, dict):
            if len(source) == 1:
                raw_items = next(iter(source.values()))
            else:
                raw_items = list(source.values())

        if not isinstance(raw_items, (list, tuple)):
            raise argument_exception(
                "source",
                f"Ожидается список элементов для десериализации, получено '{type(raw_items).__name__}'"
            )

        if context is None:
            context = {}

        result = []
        for item in raw_items:
            if item is None:
                result.append(None)
            elif isinstance(item, dict):
                # Восстановление сущности через mapping_factory
                if self.__mapping_factory is not None:
                    model = self.__mapping_factory.to_model(item, context=context)
                    result.append(model)
                elif self.__convert_factory is not None:
                    domain_conv = getattr(self.__convert_factory, "domain_convertor", None)
                    if domain_conv is not None:
                        result.append(domain_conv.deserialize(item, target_type=target_type, context=context))
                    else:
                        result.append(item)
                else:
                    result.append(item)
            elif isinstance(item, list):
                result.append(self.deserialize(item, target_type=target_type, context=context))
            else:
                result.append(item)

        return result
