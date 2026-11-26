from typing import Any, Callable, Dict, List, Optional, Tuple
from Src.Core.abstract_observer import abstract_observer
from Src.Core.event_type_enum import event_type_enum
from Src.Core.log_level_enum import log_level_enum
from Src.Core.sort_direction_enum import sort_direction_enum
from Src.Core.validator import validator
from Src.Dtos.log_query_dto import log_query_dto
from Src.Logics.observer import observer
from Src.Logics.prototype import prototype
from Src.Models.log_entry_model import log_entry_model


class log_service(abstract_observer):
    """
    Сервис сбора, хранения, фильтрации и сортировки журнала событий (Singleton)
    """

    __instance: Optional["log_service"] = None

    _event_defaults: Dict[event_type_enum, Tuple[str, log_level_enum]] = {
        event_type_enum.LOAD_SETTINGS: ("settings_manager", log_level_enum.INFO),
        event_type_enum.CHANGE_SETTINGS: ("settings_manager", log_level_enum.INFO),
        event_type_enum.SETTINGS_ERROR: ("settings_manager", log_level_enum.ERROR),
        event_type_enum.STORAGE_LOADED: ("storage_manager", log_level_enum.INFO),
        event_type_enum.ADD_ENTITY: ("storage_manager", log_level_enum.INFO),
        event_type_enum.UPDATE_ENTITY: ("storage_manager", log_level_enum.INFO),
        event_type_enum.DELETE_ENTITY: ("storage_manager", log_level_enum.INFO),
        event_type_enum.STORAGE_ERROR: ("storage_manager", log_level_enum.ERROR),
        event_type_enum.TRANSACTION_CREATED: ("warehouse", log_level_enum.INFO),
        event_type_enum.OSV_BUILT: ("warehouse", log_level_enum.INFO),
        event_type_enum.OSV_ERROR: ("warehouse", log_level_enum.ERROR),
        event_type_enum.HTTP_REQUEST_STARTED: ("web_api", log_level_enum.DEBUG),
        event_type_enum.HTTP_REQUEST_COMPLETED: ("web_api", log_level_enum.INFO),
    }

    _sort_keys: Dict[str, Callable[[log_entry_model], Any]] = {
        "period": lambda entry: entry.period,
        "subsystem": lambda entry: entry.subsystem.lower(),
        "level": lambda entry: entry.level.value,
        "event_type": lambda entry: entry.event_type.value,
        "message": lambda entry: entry.message.lower(),
    }

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(log_service, cls).__new__(cls)
            cls.__instance._initialized = False
        return cls.__instance

    def __init__(self, max_entries: int = 10000) -> None:
        if getattr(self, "_initialized", False):
            return
        validator.validate_number(max_entries, min_value=1, field_name="max_entries")
        self.__entries: List[log_entry_model] = []
        self.__max_entries: int = int(max_entries)
        observer().add(self)
        self._initialized = True

    def handle(self, event: event_type_enum, params: Optional[Dict[str, Any]] = None) -> None:
        """
        Обработка события от шины наблюдателя и сохранение записи в журнал
        """
        validator.validate_type(event, event_type_enum, field_name="event")
        if params is not None:
            validator.validate_type(params, dict, field_name="params")

        data = params or {}
        default_subsystem, default_level = self._event_defaults.get(
            event,
            ("system", log_level_enum.INFO),
        )

        subsystem = data.get("subsystem") or default_subsystem
        level = data.get("level") or default_level
        message = data.get("message") or event.value
        period = data.get("period")

        entry = log_entry_model(
            subsystem=str(subsystem),
            level=level,
            message=str(message),
            period=period,
            event_type=event,
        )
        self.__entries.append(entry)

        if len(self.__entries) > self.__max_entries:
            excess = len(self.__entries) - self.__max_entries
            del self.__entries[:excess]

    def get_all(self) -> List[log_entry_model]:
        """
        Получить копию всех записей журнала
        """
        return list(self.__entries)

    def query(self, query_dto: Optional[log_query_dto] = None) -> List[log_entry_model]:
        """
        Отфильтровать записи журнала через Прототип и отсортировать согласно параметрам запроса
        """
        if query_dto is not None:
            validator.validate_type(query_dto, log_query_dto, field_name="query_dto")

        effective_query = query_dto if query_dto is not None else log_query_dto()
        pr = prototype(list(self.__entries))

        if effective_query.filter is not None and len(effective_query.filter) > 0:
            pr = pr.clone(effective_query.filter)

        key_fn = self._sort_keys[effective_query.sort_by]
        reverse = effective_query.sort_direction == sort_direction_enum.DESC
        return sorted(pr.data, key=key_fn, reverse=reverse)

    def clear(self) -> None:
        """
        Очистить все записи журнала
        """
        self.__entries.clear()

    def ensure_subscribed(self) -> None:
        """
        Повторно зарегистрировать сервис в шине событий
        """
        observer().add(self)
