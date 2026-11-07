import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Type
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.validator import validator
from Src.Logics.convert_factory import convert_factory
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model
from Src.Models.storage_model import storage_model


class convertor:
    """
    Фасад для сериализации и десериализации данных предметной области
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(convertor, cls).__new__(cls)
            cls._instance.__factory = convert_factory()
        return cls._instance

    @property
    def factory(self) -> abstract_convert_factory:
        """
        Фабрика конвертеров данных
        """
        return self.__factory

    def serialize(self, source: Any, field_name: str = "result") -> dict:
        """
        Сериализовать объект в словарь
        """
        conv = self.__factory.create(source)
        return conv.serialize(field_name, source)

    def deserialize(
        self,
        source: Any,
        target_type: Optional[Type] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Десериализовать строку JSON, словарь или список в доменные объекты
        """
        if source is None:
            return None

        if context is None:
            context = {}

        data = source
        # Если передана JSON-строка
        if isinstance(source, str):
            clean_str = source.strip()
            if (clean_str.startswith("{") and clean_str.endswith("}")) or (
                clean_str.startswith("[") and clean_str.endswith("]")
            ):
                data = json.loads(clean_str)

        if isinstance(data, list):
            list_conv = self.__factory.create(list)
            return list_conv.deserialize(data, target_type=target_type, context=context)

        if isinstance(data, dict):
            # Проверка на составной дамп категорий хранилища
            storage_category_keys = ("range_model", "storage_key", "group_model", "nomenclature_model", "receipt_model")
            has_categories = any(k in data for k in storage_category_keys)

            if has_categories:
                return self._deserialize_storage_dump(data, context=context)

            # Одиночная доменная сущность
            domain_conv = self.__factory.create(target_type) if target_type else getattr(self.__factory, "domain_convertor")
            return domain_conv.deserialize(data, target_type=target_type, context=context)

        return data

    def _deserialize_storage_dump(
        self,
        dump: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, List[Any]]:
        """
        Десериализация составного дампа категорий с топологическим разрешением зависимостей
        """
        if context is None:
            context = {}

        result: Dict[str, List[Any]] = {}

        # 1. Единицы измерения
        raw_ranges = dump.get("range_model") or dump.get("range") or []
        if isinstance(raw_ranges, dict):
            raw_ranges = list(raw_ranges.values())
        result["range_model"] = [
            self.__factory.domain_convertor.deserialize(item, range_model, context=context)
            for item in raw_ranges
        ]

        # 2. Группы номенклатуры
        raw_groups = dump.get("group_model") or dump.get("group") or []
        if isinstance(raw_groups, dict):
            raw_groups = list(raw_groups.values())
        result["group_model"] = [
            self.__factory.domain_convertor.deserialize(item, nomenclature_group_model, context=context)
            for item in raw_groups
        ]

        # 3. Склады
        raw_storages = dump.get("storage_key") or dump.get("storage") or []
        if isinstance(raw_storages, dict):
            raw_storages = list(raw_storages.values())
        result["storage_key"] = [
            self.__factory.domain_convertor.deserialize(item, storage_model, context=context)
            for item in raw_storages
        ]

        # 4. Номенклатура (зависит от единиц и групп)
        raw_noms = dump.get("nomenclature_model") or dump.get("nomenclature") or []
        if isinstance(raw_noms, dict):
            raw_noms = list(raw_noms.values())
        result["nomenclature_model"] = [
            self.__factory.domain_convertor.deserialize(item, nomenclature_model, context=context)
            for item in raw_noms
        ]

        # 5. Технологические карты (зависят от номенклатуры и вложенных рецептов)
        raw_receipts = dump.get("receipt_model") or dump.get("receipt") or []
        if isinstance(raw_receipts, dict):
            raw_receipts = list(raw_receipts.values())
        result["receipt_model"] = [
            self.__factory.domain_convertor.deserialize(item, receipt_model, context=context)
            for item in raw_receipts
        ]

        return result

    def export_storage(self, storage, output_dir: str = "Json") -> Dict[str, str]:
        """
        Экспорт коллекций хранилища в отдельные JSON-файлы
        """
        validator.validate_type(output_dir, str, field_name="output_dir")
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        collections = {
            "ranges.json": storage.ranges,
            "groups.json": storage.groups,
            "storages.json": storage.storages,
            "nomenclatures.json": storage.nomenclatures,
            "receipts.json": storage.receipts,
        }

        generated_files: Dict[str, str] = {}
        for filename, items in collections.items():
            serialized = [self.__factory.domain_convertor.convert(item) for item in items]
            filepath = out_path / filename
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(serialized, f, ensure_ascii=False, indent=2)
            generated_files[filename] = str(filepath)

        return generated_files

    def import_storage(self, input_dir: str = "Json") -> Dict[str, List[Any]]:
        """
        Импорт коллекций доменных моделей из отдельных JSON-файлов
        """
        validator.validate_type(input_dir, str, field_name="input_dir")
        in_path = Path(input_dir)

        context: Dict[str, Any] = {}
        result: Dict[str, List[Any]] = {}

        # 1. Единицы измерения
        ranges_file = in_path / "ranges.json"
        if ranges_file.is_file():
            with open(ranges_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            result["ranges"] = [
                self.__factory.domain_convertor.deserialize(item, range_model, context=context)
                for item in data
            ]

        # 2. Группы
        groups_file = in_path / "groups.json"
        if groups_file.is_file():
            with open(groups_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            result["groups"] = [
                self.__factory.domain_convertor.deserialize(item, nomenclature_group_model, context=context)
                for item in data
            ]

        # 3. Склады
        storages_file = in_path / "storages.json"
        if storages_file.is_file():
            with open(storages_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            result["storages"] = [
                self.__factory.domain_convertor.deserialize(item, storage_model, context=context)
                for item in data
            ]

        # 4. Номенклатура
        noms_file = in_path / "nomenclatures.json"
        if noms_file.is_file():
            with open(noms_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            result["nomenclatures"] = [
                self.__factory.domain_convertor.deserialize(item, nomenclature_model, context=context)
                for item in data
            ]

        # 5. Рецепты
        receipts_file = in_path / "receipts.json"
        if receipts_file.is_file():
            with open(receipts_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            result["receipts"] = [
                self.__factory.domain_convertor.deserialize(item, receipt_model, context=context)
                for item in data
            ]

        return result
