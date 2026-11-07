import json
import os
import sys
import pytest
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Logics.convertor import convertor
from Src.Logics.storage_manager import storage_manager
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model
from Src.Models.storage_model import storage_model


class test_storage_roundtrip:
    """
    Интеграционные тесты сквозной сериализации и десериализации хранилища данных
    """

    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.facade = convertor()
        self.storage = storage_manager()
        self.storage.clear()
        self.storage.first_start()

    def test_roundtrip_storage_dump(self):
        """
        Проверка сквозного цикла сериализации хранилища в JSON и обратного восстановления
        """
        # Arrange
        serialized_wrap = self.facade.serialize(self.storage.data)
        assert "result" in serialized_wrap
        json_text = json.dumps(serialized_wrap["result"], ensure_ascii=False)

        # Act
        restored_data = self.facade.deserialize(json_text)

        # Assert
        assert isinstance(restored_data, dict)
        assert "range_model" in restored_data
        assert "nomenclature_model" in restored_data
        assert "receipt_model" in restored_data
        assert "storage_key" in restored_data

        # Проверка количества восстановленных сущностей
        assert len(restored_data["range_model"]) == len(self.storage.ranges)
        assert len(restored_data["storage_key"]) == len(self.storage.storages)
        assert len(restored_data["nomenclature_model"]) == len(self.storage.nomenclatures)
        assert len(restored_data["receipt_model"]) == len(self.storage.receipts)

        # Проверка корректности восстановления связей в рецептах
        restored_receipts = restored_data["receipt_model"]
        pizza = next((r for r in restored_receipts if r.name == "Пицца Пепперони"), None)
        assert pizza is not None
        assert isinstance(pizza, receipt_model)
        assert len(pizza.rows) > 0
        assert pizza.gross > 0

    def test_export_and_import_json_collections(self, tmp_path):
        """
        Проверка экспорта коллекций хранилища в каталог JSON и последующего импорта
        """
        # Arrange
        export_dir = str(tmp_path / "Json")

        # Act: Экспорт в файлы
        exported_files = self.facade.export_storage(self.storage, output_dir=export_dir)

        # Assert: Файлы созданы и не пустые
        assert len(exported_files) == 5
        for filename, filepath in exported_files.items():
            assert os.path.exists(filepath)
            with open(filepath, "r", encoding="utf-8") as f:
                content = json.load(f)
            assert isinstance(content, list)
            assert len(content) > 0

        # Act: Импорт из файлов
        imported = self.facade.import_storage(input_dir=export_dir)

        # Assert: Модели полностью восстановлены
        assert len(imported["ranges"]) == len(self.storage.ranges)
        assert len(imported["storages"]) == len(self.storage.storages)
        assert len(imported["groups"]) == len(self.storage.groups)
        assert len(imported["nomenclatures"]) == len(self.storage.nomenclatures)
        assert len(imported["receipts"]) == len(self.storage.receipts)
