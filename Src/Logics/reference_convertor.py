from typing import Any, Dict, Optional, Set
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_reference import abstract_reference
from Src.Core.common import common
from Src.Core.exception import argument_exception


class reference_convertor(abstract_convertor):
    """
    Конвертер доменных сущностей (наследников abstract_reference) в словарь
    """

    def __init__(self, factory: Optional[Any] = None):
        self.__factory = factory
        self.__visited: Set[int] = set()

    @property
    def factory(self) -> Optional[Any]:
        return self.__factory

    @factory.setter
    def factory(self, value: Any) -> None:
        self.__factory = value

    def convert(self, source: Any) -> Dict[str, Any]:
        """
        Преобразование доменной сущности в словарь с рекурсивным обходом свойств.

        Args:
            source: Экземпляр доменной модели

        Returns:
            Словарь наименований полей и их значений
        """
        if source is None:
            raise argument_exception("source", "Объект сущности не может быть None!")

        if not isinstance(source, abstract_reference):
            raise argument_exception(
                "source",
                f"Объект типа '{type(source).__name__}' не является наследником abstract_reference!"
            )

        source_obj_id = id(source)
        if source_obj_id in self.__visited:
            return {
                "id": getattr(source, "id", ""),
                "name": getattr(source, "name", ""),
            }

        self.__visited.add(source_obj_id)
        result: Dict[str, Any] = {}

        try:
            field_names = common.get_fields(source, is_common=False)

            for field_name in field_names:
                try:
                    raw_value = getattr(source, field_name)
                except Exception:
                    continue

                if raw_value is None:
                    result[field_name] = None
                elif self.__factory is not None:
                    conv = self.__factory.create_by_object(raw_value)
                    result[field_name] = conv.convert(raw_value)
                else:
                    if isinstance(raw_value, (int, float, str, bool)):
                        result[field_name] = raw_value
                    elif isinstance(raw_value, abstract_reference):
                        result[field_name] = self.convert(raw_value)
                    elif isinstance(raw_value, (list, tuple, set)):
                        result[field_name] = [
                            self.convert(item) if isinstance(item, abstract_reference) else item
                            for item in raw_value
                        ]
                    else:
                        result[field_name] = str(raw_value)
        finally:
            self.__visited.discard(source_obj_id)

        return result
