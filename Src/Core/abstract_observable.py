from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from Src.Core.abstract_observer import abstract_observer
from Src.Core.event_type_enum import event_type_enum


class abstract_observable(ABC):
    """
    Абстрактный интерфейс субъекта наблюдения для подписки и рассылки событий
    """

    @abstractmethod
    def add(self, source: abstract_observer) -> None:
        """
        Подписать наблюдателя на получение событий
        """
        pass

    @abstractmethod
    def delete(self, source: abstract_observer) -> None:
        """
        Отписать наблюдателя от получения событий
        """
        pass

    @abstractmethod
    def notify(self, event: event_type_enum, params: Optional[Dict[str, Any]] = None) -> None:
        """
        Оповестить всех подписанных наблюдателей о наступлении события
        """
        pass
