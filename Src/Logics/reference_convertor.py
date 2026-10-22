from typing import Any, Optional, Set
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_reference import abstract_reference
from Src.Core.common import common
from Src.Core.exception import argument_exception


class reference_convertor(abstract_convertor):
    """
    Конвертер доменных ссылок и моделей (наследников abstract_reference) в словарь
    """

    def __init__(self, factory: Optional[Any] = None):
        """
        Инициализация конвертера с опциональной фабрикой для разрешения дочерних типов
        """
        self.__factory = factory

    @property
    def factory(self) -> Optional[Any]:
        """
        Связанная фабрика конвертации
        """
        return self.__factory

    @factory.setter
    def factory(self, value: Any) -> None:
        self.__factory = value

    def convert(self, source: Any, visited: Optional[Set[int]] = None) -> dict:
        """
        Преобразование доменной сущности в словарь (field -> value) с защитой от циклических ссылок.

        Args:
            source: Экземпляр доменной модели (abstract_reference)
            visited: Множество идентификаторов посещенных объектов для предотвращения зацикливания

        Returns:
            Словарь наименований полей и их сериализованных значений
        """
        if source is None:
            raise argument_exception("source", "Объект сущности не может быть None!")

        if not isinstance(source, abstract_reference):
            raise argument_exception(
                "source",
                f"Объект типа '{type(source).__name__}' не является наследником abstract_reference!"
            )

        if visited is None:
            visited = set()

        source_obj_id = id(source)
        if source_obj_id in visited:
            # Предотвращение бесконечной рекурсии при взаимных ссылках
            return {
                "id": getattr(source, "id", ""),
                "name": getattr(source, "name", ""),
            }

        visited.add(source_obj_id)
        result = {}

        field_names = common.get_fields(source, is_common=False)

        for field_name in field_names:
            try:
                raw_value = getattr(source, field_name)
            except Exception:
                continue

            if raw_value is None:
                result[field_name] = None
            elif self.__factory is not None:
                result[field_name] = self.__factory.convert(raw_value, visited=visited)
            else:
                # Автономное преобразование без фабрики
                if isinstance(raw_value, (int, float, str, bool)):
                    result[field_name] = raw_value
                elif isinstance(raw_value, abstract_reference):
                    result[field_name] = self.convert(raw_value, visited=visited)
                elif isinstance(raw_value, (list, tuple, set)):
                    result[field_name] = [
                        self.convert(item, visited=visited) if isinstance(item, abstract_reference) else item
                        for item in raw_value
                    ]
                else:
                    result[field_name] = str(raw_value)

        visited.remove(source_obj_id)
        return result
