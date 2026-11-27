from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from Src.Core.event_type_enum import event_type_enum


class abstract_observer(ABC):
    """
    Абстрактный интерфейс наблюдателя для обработки событий подсистем
    """

    @abstractmethod
    def handle(self, event: event_type_enum, params: Optional[Dict[str, Any]] = None) -> None:
        """
        Обработать полученное событие с переданными параметрами
        """
        pass
