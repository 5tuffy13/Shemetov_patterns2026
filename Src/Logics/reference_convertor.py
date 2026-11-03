from typing import Any, Dict, Optional, Set
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_reference import abstract_reference
from Src.Core.common import common
from Src.Core.exception import argument_exception


class reference_convertor(abstract_convertor):
    """
    Конвертер доменных сущностей (наследников abstract_reference) в словарь
    """

    # Список псевдонимов свойств, исключаемых во избежание дублирования в JSON
    IGNORE_ALIASES = {"base", "value", "gross_weight", "net_weight"}

    def __init__(self, factory: Optional[abstract_convert_factory] = None):
        self.__factory = factory
        self.__visited: Set[int] = set()

    @property
    def factory(self) -> Optional[abstract_convert_factory]:
        return self.__factory

    @factory.setter
    def factory(self, value: abstract_convert_factory) -> None:
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
            return None

        self.__visited.add(source_obj_id)
        result: Dict[str, Any] = {}

        try:
            field_names = common.get_fields(source, is_common=False)

            for field_name in sorted(field_names):
                if field_name in self.IGNORE_ALIASES:
                    continue

                try:
                    raw_value = getattr(source, field_name)
                except Exception:
                    continue

                # Базовая единица измерения ссылается сама на себя или пуста
                if raw_value is None or raw_value is source:
                    result[field_name] = None
                elif self.__factory is not None:
                    convertor = self.__factory.create(type(raw_value))
                    result[field_name] = convertor.convert(raw_value)
                else:
                    if isinstance(raw_value, (int, float, str, bool)):
                        result[field_name] = raw_value
                    elif isinstance(raw_value, abstract_reference):
                        result[field_name] = self.convert(raw_value)
                    else:
                        result[field_name] = str(raw_value)
        finally:
            self.__visited.discard(source_obj_id)

        return result
