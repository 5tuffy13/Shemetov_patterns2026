from typing import Any, Dict, List, Optional
from Src.Core.abstract_observable import abstract_observable
from Src.Core.abstract_observer import abstract_observer
from Src.Core.event_type_enum import event_type_enum
from Src.Core.validator import validator


class observer(abstract_observable):
    """
    Централизованная шина событий подсистем на базе шаблона Наблюдатель (Singleton)
    """

    __instance: Optional["observer"] = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(observer, cls).__new__(cls)
            cls.__instance._initialized = False
        return cls.__instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self.__handlers: List[abstract_observer] = []
        self._initialized = True

    @property
    def handlers(self) -> List[abstract_observer]:
        """
        Копия списка зарегистрированных наблюдателей
        """
        return list(self.__handlers)

    def add(self, source: abstract_observer) -> None:
        """
        Идемпотентная подписка наблюдателя на события шины
        """
        validator.validate_type(source, abstract_observer, field_name="source")
        if any(handler is source for handler in self.__handlers) or source in self.__handlers:
            return
        self.__handlers.append(source)

    def delete(self, source: abstract_observer) -> None:
        """
        Безопасное удаление наблюдателя из списка рассылки
        """
        validator.validate_type(source, abstract_observer, field_name="source")
        self.__handlers = [
            handler for handler in self.__handlers
            if handler is not source and handler != source
        ]

    def notify(self, event: event_type_enum, params: Optional[Dict[str, Any]] = None) -> None:
        """
        Рассылка события всем подписанным наблюдателям с изоляцией сбоев обработчиков
        """
        validator.validate_type(event, event_type_enum, field_name="event")
        if params is not None:
            validator.validate_type(params, dict, field_name="params")

        payload = dict(params) if params is not None else {}
        for handler in list(self.__handlers):
            try:
                handler.handle(event, payload)
            except Exception:
                pass

    def clear(self) -> None:
        """
        Очистка всех зарегистрированных подписчиков
        """
        self.__handlers.clear()
