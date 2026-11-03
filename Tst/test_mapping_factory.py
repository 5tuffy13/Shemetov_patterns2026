import sys
import pytest
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Dtos.nomenclature_dto import nomenclature_dto
from Src.Dtos.range_dto import range_dto
from Src.Dtos.receipt_dto import receipt_dto
from Src.Dtos.storage_dto import storage_dto
from Src.Logics.mapping_factory import mapping_factory
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_row_model import receipt_row_model
from Src.Models.storage_model import storage_model


class test_mapping_factory:
    """
    Тестирование фабрики сопоставления доменных моделей и DTO
    """

    @pytest.fixture(autouse=True)
    def setup_data(self):
        # Подготовка
        self.factory = mapping_factory()
        self.unit_g = range_model("грамм", 1)
        self.unit_kg = range_model("килограмм", 1000, self.unit_g)
        self.group = nomenclature_group_model("Сырье")
        self.flour = nomenclature_model("Мука", "Мука пшеничная", self.group, self.unit_g)
        self.storage = storage_model("Склад №1", "ул. Ленина, 10")
        self.receipt = receipt_model("Тесто", portions=1, cooking_time=30)
        self.receipt.add_row(receipt_row_model(self.flour, gross=180.0, net=180.0))

    def test_success_mapping_factory_range_to_dto(self):
        """
        <summary>
        Проверка преобразования единицы измерения в DTO с корректным base_code
        </summary>
        """
        # Действие
        dto_g = self.factory.to_dto(self.unit_g)
        dto_kg = self.factory.to_dto(self.unit_kg)

        # Проверка
        assert isinstance(dto_g, range_dto)
        assert dto_g.name == "грамм"
        assert dto_g.base_code == ""

        assert isinstance(dto_kg, range_dto)
        assert dto_kg.name == "килограмм"
        assert dto_kg.base_code == self.unit_g.id

    def test_success_mapping_factory_nomenclature_to_dto(self):
        """
        <summary>
        Проверка преобразования номенклатуры в плоский DTO со строковыми кодами связей
        </summary>
        """
        # Действие
        dto = self.factory.to_dto(self.flour)

        # Проверка
        assert isinstance(dto, nomenclature_dto)
        assert dto.name == "Мука"
        assert dto.group_code == self.group.id
        assert dto.range_code == self.unit_g.id

    def test_success_mapping_factory_storage_to_dto(self):
        """
        <summary>
        Проверка преобразования склада в структуру DTO
        </summary>
        """
        # Действие
        dto = self.factory.to_dto(self.storage)

        # Проверка
        assert isinstance(dto, storage_dto)
        assert dto.name == "Склад №1"
        assert dto.address == "ул. Ленина, 10"

    def test_success_mapping_factory_receipt_to_dto(self):
        """
        <summary>
        Проверка преобразования технологической карты со строками ингредиентов в DTO
        </summary>
        """
        # Действие
        dto = self.factory.to_dto(self.receipt)

        # Проверка
        assert isinstance(dto, receipt_dto)
        assert dto.name == "Тесто"
        assert len(dto.rows) == 1
        assert dto.rows[0].nomenclature_code == self.flour.id
        assert dto.rows[0].gross == 180.0

    def test_success_mapping_factory_primitives_passthrough(self):
        """
        <summary>
        Проверка возврата примитивных типов без искажений
        </summary>
        """
        # Действие
        val_int = self.factory.to_dto(123)
        val_str = self.factory.to_dto("тест")

        # Проверка
        assert val_int == 123
        assert val_str == "тест"
