import sys
import pytest
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Logics.convertor import convertor
from Src.Logics.storage_manager import storage_manager
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model


class test_convertor:
    """
    Тестирование фасада конвертации и сериализации данных
    """

    @pytest.fixture(autouse=True)
    def setup_data(self):
        # Подготовка
        self.facade = convertor()
        self.storage = storage_manager()
        self.storage.clear()
        self.storage.first_start()

    def test_success_convertor_serialize_domain_model(self):
        """
        <summary>
        Проверка сериализации одиночной доменной модели рецепта через фасад
        </summary>
        """
        # Подготовка
        receipts = self.storage.receipts
        assert len(receipts) > 0
        pizza = receipts[0]

        # Действие
        result = self.facade.serialize(pizza)

        # Проверка
        assert isinstance(result, dict)
        assert "result" in result
        assert result["result"]["name"] == pizza.name
        assert "rows" in result["result"]

    def test_success_convertor_serialize_storage_data(self):
        """
        <summary>
        Проверка сериализации полного набора данных хранилища
        </summary>
        """
        # Действие
        result = self.facade.serialize(self.storage.data)

        # Проверка
        assert isinstance(result, dict)
        assert "result" in result
        dump = result["result"]
        assert storage_manager.range_key() in dump
        assert storage_manager.nomenclature_key() in dump
        assert storage_manager.receipt_key() in dump
        assert len(dump[storage_manager.range_key()]) > 0
