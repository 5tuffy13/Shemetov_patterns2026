from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class abstract_mapping_factory(ABC):
    """
    Интерфейс фабрики сопоставления между слоями Domain и DTO
    """

    @abstractmethod
    def to_dto(self, source: Any) -> Any:
        """
        Преобразовать доменную модель или коллекцию в DTO
        """
        pass

    @abstractmethod
    def to_model(self, source: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Преобразовать DTO в доменную модель с разрешением связей
        """
        pass
