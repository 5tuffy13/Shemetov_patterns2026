import datetime
from typing import Optional
from Src.Core.abstract_reference import abstract_reference
from Src.Core.event_type_enum import event_type_enum
from Src.Core.log_level_enum import log_level_enum
from Src.Core.validator import validator


class log_entry_model(abstract_reference):
    """
    Доменная модель записи журнала событий системы
    """

    def __init__(
        self,
        subsystem: str = "system",
        level: log_level_enum = log_level_enum.INFO,
        message: str = "-",
        period: Optional[datetime.datetime] = None,
        event_type: event_type_enum = event_type_enum.HTTP_REQUEST_COMPLETED,
        name: Optional[str] = None,
    ) -> None:
        """
        Инициализация записи журнала событий
        """
        effective_name = (
            name
            if isinstance(name, str) and name.strip()
            else (subsystem.strip()[:50] if isinstance(subsystem, str) and subsystem.strip() else None)
        )
        super().__init__(effective_name)
        self.__period: datetime.datetime = datetime.datetime.now()
        self.__subsystem: str = "system"
        self.__level: log_level_enum = log_level_enum.INFO
        self.__message: str = "-"
        self.__event_type: event_type_enum = event_type_enum.HTTP_REQUEST_COMPLETED

        self.subsystem = subsystem
        self.level = level
        self.message = message
        if period is not None:
            self.period = period
        self.event_type = event_type

    @property
    def period(self) -> datetime.datetime:
        """
        Дата и время возникновения события
        """
        return self.__period

    @period.setter
    def period(self, value: datetime.datetime) -> None:
        """
        Сеттер даты и времени события с валидацией типа
        """
        validator.validate_type(value, datetime.datetime, field_name="period")
        self.__period = value

    @property
    def subsystem(self) -> str:
        """
        Наименование подсистемы-источника события
        """
        return self.__subsystem

    @subsystem.setter
    def subsystem(self, value: str) -> None:
        """
        Сеттер подсистемы с проверкой непустой строки до 100 символов
        """
        validator.validate(value, str, 100, field_name="subsystem")
        self.__subsystem = value.strip()

    @property
    def level(self) -> log_level_enum:
        """
        Уровень значимости сообщения
        """
        return self.__level

    @level.setter
    def level(self, value: log_level_enum | str) -> None:
        """
        Сеттер уровня значимости с поддержкой строкового представления
        """
        if isinstance(value, str):
            value = log_level_enum.from_string(value)
        validator.validate_type(value, log_level_enum, field_name="level")
        self.__level = value

    @property
    def message(self) -> str:
        """
        Текстовое описание события
        """
        return self.__message

    @message.setter
    def message(self, value: str) -> None:
        """
        Сеттер текста сообщения с проверкой непустой строки до 2000 символов
        """
        validator.validate(value, str, 2000, field_name="message")
        self.__message = value.strip()

    @property
    def event_type(self) -> event_type_enum:
        """
        Классифицированный тип события подсистемы
        """
        return self.__event_type

    @event_type.setter
    def event_type(self, value: event_type_enum | str) -> None:
        """
        Сеттер типа события с поддержкой строкового представления
        """
        if isinstance(value, str):
            value = event_type_enum.from_string(value)
        validator.validate_type(value, event_type_enum, field_name="event_type")
        self.__event_type = value
