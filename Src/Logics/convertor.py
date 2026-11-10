import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Type
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.validator import validator
from Src.Logics.convert_factory import convert_factory


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

        conv = self.__factory.create(type(data))
        return conv.deserialize(data, target_type=target_type, context=context)

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
            serialized = self.__factory.create(list).convert(items)
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

        files_order = [
            ("ranges.json", "ranges"),
            ("groups.json", "groups"),
            ("storages.json", "storages"),
            ("nomenclatures.json", "nomenclatures"),
            ("receipts.json", "receipts"),
        ]

        list_conv = self.__factory.create(list)
        for filename, category_name in files_order:
            file_path = in_path / filename
            if file_path.is_file():
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                result[category_name] = list_conv.deserialize(data, context=context)

        return result
