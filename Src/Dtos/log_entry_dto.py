import datetime
from typing import Any, Dict
from Src.Core.abstract_dto import abstract_dto
from Src.Core.event_type_enum import event_type_enum
from Src.Core.log_level_enum import log_level_enum
from Src.Core.validator import validator
from Src.Models.log_entry_model import log_entry_model


class log_entry_dto(abstract_dto):
    """
    Плоская структура передачи данных (DTO) для записи журнала событий
    """

    def __init__(self) -> None:
        self.__id: str = ""
        self.__period: str = ""
        self.__subsystem: str = ""
        self.__level: str = log_level_enum.INFO.value
        self.__event_type: str = event_type_enum.HTTP_REQUEST_COMPLETED.value
        self.__message: str = ""

    @property
    def id(self) -> str:
        """
        Уникальный идентификатор записи
        """
        return self.__id

    @id.setter
    def id(self, value: str) -> None:
        validator.validate_type(value, str, field_name="id")
        self.__id = value.strip()

    @property
    def period(self) -> str:
        """
        Метка времени события в формате ISO 8601
        """
        return self.__period

    @period.setter
    def period(self, value: str) -> None:
        validator.validate(value, str, 64, field_name="period")
        self.__period = value.strip()

    @property
    def subsystem(self) -> str:
        """
        Подсистема-источник события
        """
        return self.__subsystem

    @subsystem.setter
    def subsystem(self, value: str) -> None:
        validator.validate(value, str, 100, field_name="subsystem")
        self.__subsystem = value.strip()

    @property
    def level(self) -> str:
        """
        Уровень значимости записи
        """
        return self.__level

    @level.setter
    def level(self, value: str) -> None:
        validator.validate(value, str, 20, field_name="level")
        self.__level = log_level_enum.from_string(value).value

    @property
    def event_type(self) -> str:
        """
        Идентификатор типа события
        """
        return self.__event_type

    @event_type.setter
    def event_type(self, value: str) -> None:
        validator.validate(value, str, 100, field_name="event_type")
        self.__event_type = value.strip()

    @property
    def message(self) -> str:
        """
        Текст сообщения журнала
        """
        return self.__message

    @message.setter
    def message(self, value: str) -> None:
        validator.validate(value, str, 2000, field_name="message")
        self.__message = value.strip()

    def from_domain_model(self, source: log_entry_model) -> "log_entry_dto":
        """
        Создать DTO из доменной модели записи журнала
        """
        validator.validate_type(source, log_entry_model, field_name="source")

        dto = log_entry_dto()
        dto.id = source.id
        dto.period = source.period.isoformat()
        dto.subsystem = source.subsystem
        dto.level = source.level.value
        dto.event_type = source.event_type.value
        dto.message = source.message
        return dto

    def from_dict(self, data: Dict[str, Any]) -> "log_entry_dto":
        """
        Заполнить свойства DTO из словаря
        """
        validator.validate_type(data, dict, field_name="data")

        if "id" in data and data["id"] is not None:
            self.id = str(data["id"])
        if "period" in data and data["period"] is not None:
            raw_period = data["period"]
            self.period = raw_period.isoformat() if isinstance(raw_period, datetime.datetime) else str(raw_period)
        if "subsystem" in data and data["subsystem"] is not None:
            self.subsystem = str(data["subsystem"])
        if "level" in data and data["level"] is not None:
            raw_level = data["level"]
            self.level = raw_level.value if isinstance(raw_level, log_level_enum) else str(raw_level)
        if "event_type" in data and data["event_type"] is not None:
            raw_event = data["event_type"]
            self.event_type = raw_event.value if isinstance(raw_event, event_type_enum) else str(raw_event)
        if "message" in data and data["message"] is not None:
            self.message = str(data["message"])

        return self

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразовать DTO записи журнала в словарь для сериализации
        """
        return {
            "id": self.id,
            "period": self.period,
            "subsystem": self.subsystem,
            "level": self.level,
            "event_type": self.event_type,
            "message": self.message,
            "type": self.type,
        }
