from typing import Dict, Optional, Set, Tuple
from Src.Core.abstract_reference import abstract_reference


class reference_service:
    """
    Сервис контроля ссылочной целостности сущностей на базе индекса обратных зависимостей
    """

    def __init__(self, storage=None):
        """
        Инициализация сервиса с построением хеш-индекса зависимостей O(1)
        """
        self.__storage = storage
        self.__dependency_index: Dict[str, Set[str]] = {}
        if storage is not None:
            self.rebuild(storage)

    @property
    def dependency_index(self) -> Dict[str, Set[str]]:
        """
        Индекс обратных ссылок (target_id -> множество описаний связей)
        """
        return self.__dependency_index

    def rebuild(self, storage) -> None:
        """
        Построение обратного индекса зависимостей за один проход O(N) через рефлексию
        """
        self.__storage = storage
        self.__dependency_index.clear()

        if storage is None:
            return

        for category_key in storage.keys():
            for entity in storage.get_all(category_key):
                self._index_entity_dependencies(entity)

    def _index_entity_dependencies(self, entity: abstract_reference) -> None:
        """
        Рефлексивное извлечение исходящих ссылок сущности и регистрация в обратном индексе
        """
        if not isinstance(entity, abstract_reference):
            return

        entity_name = getattr(entity, "name", entity.__class__.__name__)

        for attr in dir(entity):
            if attr.startswith("_"):
                continue
            try:
                val = getattr(entity, attr)
            except Exception:
                continue

            # Прямая ссылка на другую доменную модель
            if isinstance(val, abstract_reference) and val.id != entity.id:
                desc = self._format_description(attr, entity_name, entity.__class__.__name__)
                self._add_dependency(val.id, desc)

            # Табличная часть или список ссылок
            elif isinstance(val, list):
                for item in val:
                    for sub_attr in dir(item):
                        if sub_attr.startswith("_"):
                            continue
                        try:
                            sub_val = getattr(item, sub_attr)
                        except Exception:
                            continue
                        if isinstance(sub_val, abstract_reference) and sub_val.id != entity.id:
                            desc = self._format_description(sub_attr, entity_name, entity.__class__.__name__)
                            self._add_dependency(sub_val.id, desc)

    def _format_description(self, attr_name: str, parent_name: str, parent_type: str) -> str:
        """
        Формирование описания связи по имени атрибута и имени родительской сущности
        """
        if attr_name == "base_range":
            return f"используется как базовая для единицы измерения '{parent_name}'"
        if attr_name == "group":
            return f"используется в номенклатуре '{parent_name}'"
        if attr_name == "range":
            if "receipt" in parent_type.lower():
                return f"используется в рецепте '{parent_name}'"
            return f"используется в номенклатуре '{parent_name}'"
        if attr_name == "nomenclature":
            return f"используется в рецепте '{parent_name}'"
        if attr_name == "receipt":
            return f"используется как полуфабрикат в рецепте '{parent_name}'"
        return f"связан с {parent_type} '{parent_name}'"

    def _add_dependency(self, target_id: str, description: str) -> None:
        """
        Добавить зависимость в индекс обратных ссылок O(1)
        """
        if not target_id:
            return
        if target_id not in self.__dependency_index:
            self.__dependency_index[target_id] = set()
        self.__dependency_index[target_id].add(description)

    def can_delete(self, identifier: str) -> Tuple[bool, str]:
        """
        Проверка ссылочной целостности за O(1) через поиск в индексе зависимостей
        """
        if not identifier:
            return False, "Не указан идентификатор сущности"

        target_id = identifier.id if isinstance(identifier, abstract_reference) else str(identifier)

        if self.__storage is not None:
            for cat in self.__storage.keys():
                found = self.__storage.get_by_id(cat, target_id) or self.__storage.get_by_name(cat, target_id)
                if found:
                    target_id = found.id
                    break

        dependents = self.__dependency_index.get(target_id)
        if dependents:
            reason = "; ".join(sorted(dependents))
            return False, f"Запрещено удалять сущность: {reason}"

        return True, ""
