import sys
import pytest
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Logics.convertor import convertor
from Src.Logics.storage_manager import storage_manager
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model
from Src.Models.storage_model import storage_model


class test_deserialization:
    """
    Набор тестов для десериализации отдельных доменных сущностей
    """

    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.facade = convertor()
        self.storage = storage_manager()
        self.storage.clear()
        self.storage.first_start()

    def test_deserialize_range_model(self):
        """
        Проверка десериализации единицы измерения из сериализованного представления
        """
        # Arrange
        kg = self.storage.get_range("килограмм")
        assert kg is not None
        serialized = self.facade.factory.domain_convertor.convert(kg)
        context = {kg.base_range.id: kg.base_range}

        # Act
        restored = self.facade.deserialize(serialized, target_type=range_model, context=context)

        # Assert
        assert isinstance(restored, range_model)
        assert restored.id == kg.id
        assert restored.name == kg.name
        assert restored.coeff == kg.coeff
        assert restored.base_range.id == kg.base_range.id

    def test_deserialize_storage_model(self):
        """
        Проверка десериализации склада
        """
        # Arrange
        st = self.storage.storages[0]
        serialized = self.facade.factory.domain_convertor.convert(st)

        # Act
        restored = self.facade.deserialize(serialized, target_type=storage_model)

        # Assert
        assert isinstance(restored, storage_model)
        assert restored.id == st.id
        assert restored.name == st.name
        assert restored.address == st.address

    def test_deserialize_group_model(self):
        """
        Проверка десериализации группы номенклатуры
        """
        # Arrange
        group = self.storage.groups[0]
        serialized = self.facade.factory.domain_convertor.convert(group)

        # Act
        restored = self.facade.deserialize(serialized, target_type=nomenclature_group_model)

        # Assert
        assert isinstance(restored, nomenclature_group_model)
        assert restored.id == group.id
        assert restored.name == group.name

    def test_deserialize_nomenclature_model(self):
        """
        Проверка десериализации номенклатуры с восстановлением ссылок на группу и единицу
        """
        # Arrange
        flour = self.storage.get_nomenclature("Мука пшеничная")
        assert flour is not None
        serialized = self.facade.factory.domain_convertor.convert(flour)
        context = {
            flour.group.id: flour.group,
            flour.range.id: flour.range,
        }

        # Act
        restored = self.facade.deserialize(serialized, target_type=nomenclature_model, context=context)

        # Assert
        assert isinstance(restored, nomenclature_model)
        assert restored.id == flour.id
        assert restored.name == flour.name
        assert restored.full_name == flour.full_name
        assert restored.group.id == flour.group.id
        assert restored.range.id == flour.range.id

    def test_deserialize_receipt_model(self):
        """
        Проверка десериализации технологической карты с восстановлением состава ингредиентов
        """
        # Arrange
        pizza = self.storage.get_receipt("Пицца Пепперони")
        assert pizza is not None
        serialized = self.facade.factory.domain_convertor.convert(pizza)

        context = {}
        for nom in self.storage.nomenclatures:
            context[nom.id] = nom
        for rcp in self.storage.receipts:
            context[rcp.id] = rcp

        # Act
        restored = self.facade.deserialize(serialized, target_type=receipt_model, context=context)

        # Assert
        assert isinstance(restored, receipt_model)
        assert restored.id == pizza.id
        assert restored.name == pizza.name
        assert restored.portions == pizza.portions
        assert restored.cooking_time == pizza.cooking_time
        assert len(restored.rows) == len(pizza.rows)
        assert restored.gross == pizza.gross
        assert restored.net == pizza.net
