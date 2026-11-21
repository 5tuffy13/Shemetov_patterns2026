from typing import Any, Dict, List, Optional
from Src.Core.validator import validator
from Src.Dtos.filter_item_dto import filter_item_dto


class filter_dto:
    """
    DTO составного фильтра данных со списком условий
    """

    def __init__(self, items: Optional[List[filter_item_dto]] = None, entity_type: str = ""):
        """
        Инициализация составного фильтра
        """
        self.__items: List[filter_item_dto] = []
        self.__entity_type: str = str(entity_type).strip() if entity_type else ""

        if items is not None:
            for item in items:
                self.add_item(item)

    @property
    def items(self) -> List[filter_item_dto]:
        """
        Список элементов фильтра
        """
        return self.__items

    @property
    def filters(self) -> List[filter_item_dto]:
        """
        Псевдоним списка условий фильтрации
        """
        return self.__items

    @filters.setter
    def filters(self, new_items: List[filter_item_dto]):
        """
        Сеттер списка условий
        """
        validator.validate(new_items, list, field_name="filters")
        self.__items.clear()
        for it in new_items:
            self.add_item(it)

    @property
    def entity_type(self) -> str:
        """
        Тип целевой доменной сущности
        """
        return self.__entity_type

    @entity_type.setter
    def entity_type(self, val: str):
        """
        Сеттер типа целевой сущности
        """
        self.__entity_type = str(val).strip() if val else ""

    def add_item(self, item: Any) -> None:
        """
        Добавить условие в составной фильтр
        """
        if isinstance(item, filter_item_dto):
            self.__items.append(item)
        elif isinstance(item, dict):
            self.__items.append(filter_item_dto.from_dict(item))

    def __iter__(self):
        """
        Итератор по элементам фильтра
        """
        return iter(self.__items)

    def __len__(self) -> int:
        """
        Количество условий в фильтре
        """
        return len(self.__items)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "filter_dto":
        """
        Фабричный метод создания составного фильтра из словаря
        """
        validator.validate(data, dict, field_name="data")
        instance = cls(entity_type=data.get("entity_type", ""))

        raw_items = data.get("items") or data.get("filters") or []
        if isinstance(raw_items, list):
            for raw_item in raw_items:
                instance.add_item(raw_item)
        # Если передан единичный критерий прямо в корне словаря
        elif "field_name" in data or "field" in data:
            instance.add_item(data)

        return instance
