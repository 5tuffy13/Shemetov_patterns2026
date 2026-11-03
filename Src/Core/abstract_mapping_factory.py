from abc import ABC, abstractmethod


class abstract_mapping_factory(ABC):
    """
    Абстрактная фабрика сопоставления доменных моделей и DTO
    """

    @abstractmethod
    def to_dto(self, source: object) -> object:
        """
        Сконвертировать доменную модель в DTO
        """
        pass

    @abstractmethod
    def to_model(self, source: object) -> object:
        """
        Сконвертировать DTO в доменную модель
        """
        pass
