import datetime
import pytest
from Src.Core.exception import argument_exception
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model
from Src.Models.transaction_model import transaction_model


class test_transaction_model:
    """
    Модульные тесты доменной модели складской транзакции
    """

    @pytest.fixture(autouse=True)
    def setup_entities(self):
        self.storage = storage_model("Склад сырья")
        self.group = nomenclature_group_model("Бакалея")
        self.range = range_model("кг", 1)
        self.nom = nomenclature_model("Мука", "Мука пшеничная", self.group, self.range)

    def test_success_transaction_creation(self):
        """
        Проверка корректного создания складской проводки
        """
        # Arrange & Act
        now = datetime.datetime.now()
        tx = transaction_model(
            name="Приходная накладная №1",
            storage=self.storage,
            nomenclature=self.nom,
            range_item=self.range,
            value=150.5,
            period=now,
        )

        # Assert
        assert tx.storage == self.storage
        assert tx.nomenclature == self.nom
        assert tx.range == self.range
        assert tx.value == 150.5
        assert tx.period == now

    def test_fail_transaction_zero_value(self):
        """
        Проверка запрета создания транзакции с нулевым значением
        """
        # Arrange & Act & Assert
        with pytest.raises(argument_exception):
            transaction_model(
                storage=self.storage,
                nomenclature=self.nom,
                range_item=self.range,
                value=0.0,
            )

    def test_fail_transaction_invalid_storage_type(self):
        """
        Проверка валидации типа связанного склада
        """
        tx = transaction_model()
        with pytest.raises(argument_exception):
            tx.storage = "Некорректный склад"
