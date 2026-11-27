from enum import Enum
from Src.Core.exception import argument_exception


class event_type_enum(Enum):
    """
    Перечисление доменных и системных событий подсистем приложения
    """

    LOAD_SETTINGS = "load_settings"
    CHANGE_SETTINGS = "change_settings"
    SETTINGS_ERROR = "settings_error"

    STORAGE_LOADED = "storage_loaded"
    ADD_ENTITY = "add_entity"
    UPDATE_ENTITY = "update_entity"
    DELETE_ENTITY = "delete_entity"
    STORAGE_ERROR = "storage_error"

    TRANSACTION_CREATED = "transaction_created"
    OSV_BUILT = "osv_built"
    OSV_ERROR = "osv_error"

    HTTP_REQUEST_STARTED = "http_request_started"
    HTTP_REQUEST_COMPLETED = "http_request_completed"

    @classmethod
    def from_string(cls, value: str) -> "event_type_enum":
        """
        Преобразование строкового идентификатора в элемент перечисления событий
        """
        if not isinstance(value, str):
            raise argument_exception("value", "Тип события должен быть строкой!")

        normalized_raw = value.strip()
        if not normalized_raw:
            raise argument_exception("value", "Тип события не может быть пустым!")

        normalized_upper = normalized_raw.upper()
        normalized_lower = normalized_raw.lower()
        for item in cls:
            if item.name == normalized_upper or item.value == normalized_lower:
                return item

        raise argument_exception("value", f"Неизвестный тип события '{value}'!")
