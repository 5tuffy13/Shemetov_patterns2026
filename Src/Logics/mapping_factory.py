from typing import Any, Dict, Optional, Tuple, Type
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
    Фабрика двустороннего сопоставления доменных моделей и DTO на основе реестра типов
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

        # Реестр строковых типов для точного разрешения сущностей за O(1)
        self.__type_registry: Dict[str, Tuple[Type[abstract_reference], Type[abstract_dto]]] = {}
        for domain_cls, dto_cls in self.__domain_to_dto.items():
            self.__type_registry[domain_cls.__name__] = (domain_cls, dto_cls)
            self.__type_registry[dto_cls.__name__] = (domain_cls, dto_cls)
            self.__type_registry[f"{domain_cls.__module__}.{domain_cls.__qualname__}"] = (domain_cls, dto_cls)
            self.__type_registry[f"{dto_cls.__module__}.{dto_cls.__qualname__}"] = (domain_cls, dto_cls)

        self.__initialized = True

    def get_dto_type(self, domain_type: type) -> Optional[Type[abstract_dto]]:
        """
        Получить тип DTO по типу доменной модели
        """
        return self.__domain_to_dto.get(domain_type)

    def get_domain_type(self, dto_type: type) -> Optional[Type[abstract_reference]]:
        """
        Получить тип доменной модели по типу DTO
        """
        return self.__dto_to_domain.get(dto_type)

    def resolve_types_by_name(self, type_name: str) -> Optional[Tuple[Type[abstract_reference], Type[abstract_dto]]]:
        """
        Разрешить строковый тип в пару (domain_cls, dto_cls) за O(1)
        """
        if not isinstance(type_name, str):
            return None
        return self.__type_registry.get(type_name.strip())

    def to_dto(self, source: Any) -> Any:
        """
        Преобразовать доменную модель или коллекцию в DTO
        """
        if source is None:
            return None

        if isinstance(source, (int, float, str, bool)):
            return source

        if isinstance(source, (list, tuple, set)):
            return [self.to_dto(item) for item in source]

        if isinstance(source, dict):
            return {str(k): self.to_dto(v) for k, v in source.items()}

        source_type = type(source)
        if source_type in self.__domain_to_dto:
            dto_cls = self.__domain_to_dto[source_type]
            return dto_cls().from_domain_model(source)

        if isinstance(source, abstract_dto):
            return source

        return source

    def to_model(self, source: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Преобразовать DTO или структуру словаря в доменную модель по типу сущности
        """
        if source is None:
            return None

        if isinstance(source, (list, tuple)):
            return [self.to_model(item, context) for item in source]

        # Если передан словарь, определяем тип по полю type
        if isinstance(source, dict):
            type_val = source.get("type")
            if type_val:
                pair = self.resolve_types_by_name(str(type_val))
                if pair is not None:
                    _, dto_cls = pair
                    dto_instance = dto_cls().from_dict(source)
                    return self.to_model(dto_instance, context)
            return source

        if isinstance(source, abstract_reference):
            if context is not None and hasattr(source, "id"):
                context[source.id] = source
            return source

        # 1. Единица измерения
        if isinstance(source, range_dto):
            model = range_model(name=source.name, coeff=source.coeff)
            model.id = source.id
            if source.base_code and context and source.base_code in context:
                model.base_range = context[source.base_code]
            else:
                model.base_range = model
            if context is not None:
                context[model.id] = model
                context[model.name] = model
            return model

        # 2. Склад
        if isinstance(source, storage_dto):
            model = storage_model(name=source.name, address=source.address)
            model.id = source.id
            if context is not None:
                context[model.id] = model
                context[model.name] = model
            return model

        # 3. Группа номенклатуры
        if isinstance(source, nomenclature_group_dto):
            model = nomenclature_group_model(name=source.name)
            model.id = source.id
            if context is not None:
                context[model.id] = model
                context[model.name] = model
            return model

        # 4. Организация
        if isinstance(source, organization_dto):
            model = organization_model()
            model.id = source.id
            model.name = source.name
            model.inn = source.inn
            model.bik = source.bik
            model.account = source.account
            model.ownership_form = source.ownership_form
            if context is not None:
                context[model.id] = model
            return model

        # 5. Номенклатура
        if isinstance(source, nomenclature_dto):
            group_obj = context.get(source.group_code) if context else None
            range_obj = context.get(source.range_code) if context else None
            model = nomenclature_model(
                name=source.name,
                full_name=source.full_name,
                group=group_obj,
                range=range_obj,
            )
            model.id = source.id
            if context is not None:
                context[model.id] = model
                context[model.name] = model
            return model

        # 6. Строка рецепта
        if isinstance(source, receipt_row_dto):
            nom_obj = context.get(source.nomenclature_code) if context else None
            sub_rcp = context.get(source.receipt_code) if context else None
            row = receipt_row_model(
                nomenclature=nom_obj,
                receipt=sub_rcp,
                gross=source.gross,
                net=source.net,
            )
            row.id = source.id
            if source.name:
                row.name = source.name
            return row

        # 7. Технологическая карта (рецепт)
        if isinstance(source, receipt_dto):
            restored_rows = []
            for r in source.rows:
                restored_row = self.to_model(r, context)
                if restored_row is not None:
                    restored_rows.append(restored_row)

            model = receipt_model(
                name=source.name,
                portions=source.portions,
                cooking_time=source.cooking_time,
                rows=restored_rows,
            )
            model.id = source.id
            if context is not None:
                context[model.id] = model
                context[model.name] = model
            return model

        return source
