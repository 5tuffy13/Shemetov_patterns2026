from typing import Any, Dict, Optional
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import argument_exception


class dictionary_convertor(abstract_convertor):
    """
    Конвертер словарей для сериализации и десериализации
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

    def convert(self, source: Any) -> Dict[str, Any]:
        """
        Преобразование словаря в сериализуемый словарь со строковыми ключами.

        Args:
            source: Исходный словарь

        Returns:
            Сериализованный словарь
        """
        if source is None:
            return {}

        if not isinstance(source, dict):
            raise argument_exception(
                "source",
                f"Тип '{type(source).__name__}' не является словарем!"
            )

        result = {}
        for key, value in source.items():
            str_key = str(key)
            if value is None:
                result[str_key] = None
            elif self.__factory is not None:
                convertor = self.__factory.create(type(value))
                result[str_key] = convertor.convert(value)
            else:
                result[str_key] = value

        return result

    def deserialize(
        self,
        source: Any,
        target_type: Optional[type] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Десериализация словаря с полиморфной диспетчеризацией по фабрике
        """
        if source is None:
            return {}

        if not isinstance(source, dict):
            raise argument_exception(
                "source",
                f"Тип '{type(source).__name__}' не является словарем!"
            )

        if context is None:
            context = {}

        # 1. Если словарь представляет собой единичную сущность со свойством type
        if "type" in source and self.__factory is not None:
            mf = getattr(self.__factory, "mapping_factory", None)
            if mf is not None:
                return mf.to_model(source, context=context)

        # 2. Если словарь представляет собой контейнер коллекций (например, категории хранилища)
        # Обрабатываем ключи в порядке разрешения зависимостей (базовые справочники -> номенклатура -> рецепты)
        def _get_priority(key_name: str) -> int:
            k = str(key_name).lower()
            if any(term in k for term in ("range", "group", "storage")):
                return 0
            if "nomenclature" in k:
                return 1
            if "receipt" in k:
                return 2
            return 3

        sorted_keys = sorted(source.keys(), key=_get_priority)
        result: Dict[str, Any] = {}

        for key in sorted_keys:
            str_key = str(key)
            value = source[key]

            if value is None:
                result[str_key] = None
            elif isinstance(value, (list, tuple)) and self.__factory is not None:
                list_conv = self.__factory.create(list)
                result[str_key] = list_conv.deserialize(value, target_type=target_type, context=context)
            elif isinstance(value, dict) and self.__factory is not None:
                if "type" in value:
                    mf = getattr(self.__factory, "mapping_factory", None)
                    result[str_key] = mf.to_model(value, context=context) if mf else value
                else:
                    result[str_key] = self.deserialize(value, target_type=target_type, context=context)
            else:
                result[str_key] = value

        return result
