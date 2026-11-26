from typing import Any, Dict, Optional
from Src.Core.exception import argument_exception
from Src.Core.sort_direction_enum import sort_direction_enum
from Src.Core.validator import validator
from Src.Dtos.filter_dto import filter_dto


class log_query_dto:
    """
    Структура параметров запроса фильтрации и сортировки журнала событий
    """

    ALLOWED_SORT_FIELDS = {"period", "subsystem", "level", "event_type", "message"}

    def __init__(
        self,
        filter_obj: Optional[filter_dto] = None,
        sort_by: str = "period",
        sort_direction: sort_direction_enum = sort_direction_enum.DESC,
    ) -> None:
        self.__filter: Optional[filter_dto] = None
        self.__sort_by: str = "period"
        self.__sort_direction: sort_direction_enum = sort_direction_enum.DESC

        self.filter = filter_obj
        self.sort_by = sort_by
        self.sort_direction = sort_direction

    @property
    def filter(self) -> Optional[filter_dto]:
        """
        Составной фильтр условий отбора записей
        """
        return self.__filter

    @filter.setter
    def filter(self, value: Optional[filter_dto]) -> None:
        if value is not None:
            validator.validate_type(value, filter_dto, field_name="filter")
        self.__filter = value

    @property
    def sort_by(self) -> str:
        """
        Поле сортировки записей журнала
        """
        return self.__sort_by

    @sort_by.setter
    def sort_by(self, value: str) -> None:
        validator.validate(value, str, 50, field_name="sort_by")
        normalized = value.strip().lower()
        if normalized not in self.ALLOWED_SORT_FIELDS:
            raise argument_exception(
                "sort_by",
                f"Недопустимое поле сортировки '{value}'. Допустимые поля: {', '.join(sorted(self.ALLOWED_SORT_FIELDS))}",
            )
        self.__sort_by = normalized

    @property
    def sort_direction(self) -> sort_direction_enum:
        """
        Направление сортировки записей
        """
        return self.__sort_direction

    @sort_direction.setter
    def sort_direction(self, value: sort_direction_enum | str) -> None:
        if isinstance(value, str):
            value = sort_direction_enum.from_string(value)
        validator.validate_type(value, sort_direction_enum, field_name="sort_direction")
        self.__sort_direction = value

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "log_query_dto":
        """
        Создать параметры запроса журнала из словаря
        """
        validator.validate_type(data, dict, field_name="data")

        filter_obj = None
        if "items" in data or "filters" in data:
            filter_obj = filter_dto.from_dict(data)

        raw_sort_by = data.get("sort_by")
        if raw_sort_by is None or (isinstance(raw_sort_by, str) and not raw_sort_by.strip()):
            sort_by = "period"
        else:
            sort_by = raw_sort_by

        raw_sort_dir = data.get("sort_direction")
        if raw_sort_dir is None:
            sort_direction = sort_direction_enum.DESC
        else:
            sort_direction = raw_sort_dir

        return cls(filter_obj=filter_obj, sort_by=sort_by, sort_direction=sort_direction)
