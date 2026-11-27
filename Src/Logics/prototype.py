import datetime
from enum import Enum
from typing import Any, List, Optional
from Src.Core.abstract_prototype import abstract_prototype
from Src.Core.abstract_reference import abstract_reference
from Src.Core.validator import validator
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_item_dto import filter_item_dto
from Src.Dtos.filter_type_enum import filter_type_enum


class prototype(abstract_prototype):
    """
    Универсальная реализация паттерна Прототип для фильтрации и клонирования наборов доменных сущностей
    """

    def __init__(self, data: Optional[List[Any]] = None):
        """
        Инициализация прототипа с коллекцией данных
        """
        self.__data: List[Any] = list(data) if data is not None else []

    @property
    def data(self) -> List[Any]:
        """
        Текущая коллекция элементов прототипа
        """
        return self.__data

    def clone(self, filter_instance: Optional[filter_dto] = None) -> "prototype":
        """
        Создание независимого отфильтрованного клона прототипа
        """
        if filter_instance is None or len(filter_instance.items) == 0:
            return prototype(list(self.__data))

        filtered_items: List[Any] = []
        for item in self.__data:
            if self._matches_filter(item, filter_instance):
                filtered_items.append(item)

        return prototype(filtered_items)

    def _matches_filter(self, item: Any, filter_instance: filter_dto) -> bool:
        """
        Проверка соответствия объекта всем критериям составного фильтра (AND)
        """
        for filter_item in filter_instance.items:
            if not self._matches_item(item, filter_item):
                return False
        return True

    def _matches_item(self, item: Any, filter_item: filter_item_dto) -> bool:
        """
        Проверка соответствия объекта единичному условию фильтра
        """
        field_name = filter_item.field_name
        expected_value = filter_item.value
        op = filter_item.filter_type

        # Извлечение фактических значений (с поддержкой вложенных путей и связей)
        actual_values = self._extract_field_values(item, field_name)
        if not actual_values:
            return False

        # Если хотя бы одно из извлеченных значений удовлетворяет условию
        for actual in actual_values:
            if self._compare_values(actual, expected_value, op):
                return True

        return False

    def _extract_field_values(self, item: Any, field_path: str) -> List[Any]:
        """
        Рефлексивное извлечение значений поля с поддержкой точечной нотации и вложенных структур
        """
        if item is None or not field_path:
            return []

        # 1. Поддержка точечной нотации (например: range.base_range.name)
        if "." in field_path:
            current_targets = [item]
            for part in field_path.split("."):
                next_targets = []
                for target in current_targets:
                    val = self._get_single_attribute(target, part)
                    if val is not None:
                        if isinstance(val, list):
                            next_targets.extend(val)
                        else:
                            next_targets.append(val)
                current_targets = next_targets
                if not current_targets:
                    break
            return current_targets

        # 2. Прямое получение атрибута с текущего объекта
        val = self._get_single_attribute(item, field_path)
        if val is not None:
            # Если значение само является ссылочной моделью (например, group или range)
            if isinstance(val, abstract_reference):
                return [val, val.id, getattr(val, "name", "")]
            return [val]

        # 3. Поиск во вложенных структурах (требование № 4)
        nested_values: List[Any] = []
        for attr_name in dir(item):
            if attr_name.startswith("_"):
                continue
            try:
                sub_obj = getattr(item, attr_name)
            except Exception:
                continue

            if isinstance(sub_obj, abstract_reference) and sub_obj != item:
                # Проверяем совпадение целевого поля во вложенном объекте
                sub_val = self._get_single_attribute(sub_obj, field_path)
                if sub_val is not None:
                    nested_values.append(sub_val)

        return nested_values

    def _get_single_attribute(self, target: Any, attr_name: str) -> Any:
        """
        Безопасное извлечение значения атрибута с учетом псевдонимов
        """
        if target is None:
            return None

        # Псевдонимы уникального кода
        if attr_name in ("unique_code", "code") and hasattr(target, "id"):
            return target.id

        # Прямое обращение по свойству
        if hasattr(target, attr_name):
            try:
                return getattr(target, attr_name)
            except Exception:
                pass

        # Для словарей
        if isinstance(target, dict) and attr_name in target:
            return target[attr_name]

        return None

    def _parse_datetime_value(self, raw_value: str) -> Optional[datetime.datetime]:
        """
        Разбор строковой даты и времени в объект datetime
        """
        clean_str = raw_value.strip()
        if not clean_str:
            return None

        try:
            return datetime.datetime.fromisoformat(clean_str)
        except ValueError:
            pass

        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d.%m.%Y %H:%M:%S", "%d.%m.%Y"):
            try:
                return datetime.datetime.strptime(clean_str, fmt)
            except ValueError:
                pass
        return None

    def _compare_values(self, actual: Any, expected: Any, op: filter_type_enum) -> bool:
        """
        Сравнение фактического значения с ожидаемым согласно операции фильтра
        """
        if actual is None:
            return False

        if isinstance(actual, Enum):
            expected_clean = str(expected.value if isinstance(expected, Enum) else expected).strip().lower()
            actual_val = str(actual.value).strip().lower()
            actual_name = str(actual.name).strip().lower()
            if op == filter_type_enum.EQUALS:
                return actual_val == expected_clean or actual_name == expected_clean
            if op == filter_type_enum.LIKE:
                return expected_clean in actual_val or expected_clean in actual_name
            return False

        if isinstance(actual, datetime.datetime) and op != filter_type_enum.LIKE:
            parsed_expected = None
            if isinstance(expected, datetime.datetime):
                parsed_expected = expected
            elif isinstance(expected, datetime.date):
                parsed_expected = datetime.datetime.combine(expected, datetime.time.min)
            elif isinstance(expected, str):
                parsed_expected = self._parse_datetime_value(expected)

            if parsed_expected is not None:
                if op == filter_type_enum.EQUALS:
                    return actual == parsed_expected
                if op == filter_type_enum.GREATER:
                    return actual > parsed_expected
                if op == filter_type_enum.LESS:
                    return actual < parsed_expected
                if op == filter_type_enum.GREATER_OR_EQUAL:
                    return actual >= parsed_expected
                if op == filter_type_enum.LESS_OR_EQUAL:
                    return actual <= parsed_expected

        # Приведение к строкам для текстовых операций
        actual_str = str(actual).strip()
        expected_str = str(expected).strip()

        if op == filter_type_enum.EQUALS:
            if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
                return actual == expected
            return actual_str.lower() == expected_str.lower()

        if op == filter_type_enum.LIKE:
            return expected_str.lower() in actual_str.lower()

        # Числовые и хронологические сравнения
        try:
            if op == filter_type_enum.GREATER:
                return actual > expected
            if op == filter_type_enum.LESS:
                return actual < expected
            if op == filter_type_enum.GREATER_OR_EQUAL:
                return actual >= expected
            if op == filter_type_enum.LESS_OR_EQUAL:
                return actual <= expected
        except TypeError:
            pass

        return False

    def __len__(self) -> int:
        """
        Количество элементов в прототипе
        """
        return len(self.__data)

    def __iter__(self):
        """
        Итератор по элементам прототипа
        """
        return iter(self.__data)
