from typing import Any, Dict, Type
from Src.Core.abstract_dto import abstract_dto
from Src.Core.abstract_mapping_factory import abstract_mapping_factory
from Src.Core.abstract_reference import abstract_reference
from Src.Dtos.nomenclature_dto import nomenclature_dto
from Src.Dtos.nomenclature_group_dto import nomenclature_group_dto
from Src.Dtos.organization_dto import organization_dto
from Src.Dtos.range_dto import range_dto
from Src.Dtos.receipt_dto import receipt_dto
from Src.Dtos.receipt_row_dto import receipt_row_dto
from Src.Dtos.storage_dto import storage_dto
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.organization_model import organization_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_row_model import receipt_row_model
from Src.Models.storage_model import storage_model


class mapping_factory(abstract_mapping_factory):
    """
    Фабрика сопоставления доменных моделей и DTO
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(mapping_factory, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_mapping_factory__initialized", False):
            return

        super().__init__()

        # Прямое сопоставление: Доменная модель -> Класс DTO
        self.__domain_to_dto: Dict[Type[abstract_reference], Type[abstract_dto]] = {
            range_model: range_dto,
            storage_model: storage_dto,
            nomenclature_group_model: nomenclature_group_dto,
            nomenclature_model: nomenclature_dto,
            organization_model: organization_dto,
            receipt_row_model: receipt_row_dto,
            receipt_model: receipt_dto,
        }

        # Обратное сопоставление: Класс DTO -> Доменная модель
        self.__dto_to_domain: Dict[Type[abstract_dto], Type[abstract_reference]] = {
            dto_cls: domain_cls for domain_cls, dto_cls in self.__domain_to_dto.items()
        }

        self.__initialized = True

    def to_dto(self, source: Any) -> Any:
        """
        Преобразовать доменную модель или коллекцию в DTO
        """
        if source is None:
            return None

        # Примитивные типы возвращаются как есть
        if isinstance(source, (int, float, str, bool)):
            return source

        # Коллекции рекурсивно преобразуются
        if isinstance(source, (list, tuple, set)):
            return [self.to_dto(item) for item in source]

        if isinstance(source, dict):
            return {str(k): self.to_dto(v) for k, v in source.items()}

        # Доменные сущности
        source_type = type(source)
        if source_type in self.__domain_to_dto:
            dto_cls = self.__domain_to_dto[source_type]
            return dto_cls().from_domain_model(source)

        # Если уже является DTO
        if isinstance(source, abstract_dto):
            return source

        return source

    def to_model(self, source: Any) -> Any:
        """
        Преобразовать DTO в доменную модель
        """
        if source is None:
            return None

        source_type = type(source)
        if source_type in self.__dto_to_domain:
            domain_cls = self.__dto_to_domain[source_type]
            # Базовое создание модели
            return domain_cls(source.name) if hasattr(source, "name") else domain_cls()

        return source
