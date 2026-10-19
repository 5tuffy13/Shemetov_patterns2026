import sys
import pytest
from pathlib import Path

# Определение корня проекта
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Core.common import common
from Src.Core.exception import argument_exception
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_row_model import receipt_row_model


class TestCommon:
    """
    Набор тестов для методов интроспекции и рефлексии класса common
    """

    @pytest.fixture(autouse=True)
    def setup_data(self):
        """
        Инициализация тестовых данных
        """
        # Подготовка
        self.group = nomenclature_group_model("Сырье")
        self.unit_g = range_model("грамм", 1)
        self.flour = nomenclature_model("Мука", "Мука пшеничная", self.group, self.unit_g)
        self.water = nomenclature_model("Вода", "Вода питьевая", self.group, self.unit_g)

        self.receipt = receipt_model("Тесто", portions=1, cooking_time=30)
        self.receipt.add_row(receipt_row_model(self.flour, gross=180.0, net=180.0))
        self.receipt.add_row(receipt_row_model(self.water, gross=110.0, net=110.0))

    def test_success_common_get_fields_scalar_only(self):
        """
        <summary>
        Проверка получения только скалярных свойств модели (is_common=True)
        </summary>
        """
        # Подготовка
        target = self.receipt

        # Действие
        fields = common.get_fields(target, is_common=True)

        # Проверка
        assert "name" in fields
        assert "portions" in fields
        assert "cooking_time" in fields
        assert "gross" in fields
        assert "net" in fields
        # Коллекционное свойство rows должно быть исключено
        assert "rows" not in fields

    def test_success_common_get_fields_all(self):
        """
        <summary>
        Проверка получения всех свойств включая коллекции (is_common=False)
        </summary>
        """
        # Подготовка
        target = self.receipt

        # Действие
        fields = common.get_fields(target, is_common=False)

        # Проверка
        assert "rows" in fields
        assert "name" in fields

    def test_success_common_get_entity_header(self):
        """
        <summary>
        Проверка формирования заголовка сущности со скалярными свойствами
        </summary>
        """
        # Подготовка
        target = self.flour

        # Действие
        headers = common.get_entity_header(target)

        # Проверка
        assert len(headers) > 0
        field_map = {h.field: h.value for h in headers}
        assert field_map["name"] == "Мука"
        assert field_map["full_name"] == "Мука пшеничная"

    def test_success_common_get_entity_table_empty_for_simple_entity(self):
        """
        <summary>
        Проверка возврата пустой таблицы для сущностей без коллекционных агрегатов
        </summary>
        """
        # Подготовка
        target = self.unit_g

        # Действие
        table = common.get_entity_table(target)

        # Проверка
        assert len(table) == 0

    def test_success_common_get_entity_table_aggregate(self):
        """
        <summary>
        Проверка извлечения табличной части для агрегата с коллекцией (рецепт)
        </summary>
        """
        # Подготовка
        target = self.receipt

        # Действие
        table = common.get_entity_table(target)

        # Проверка
        assert len(table) == 2  # Две строки ингредиентов
        first_row = table[0]
        assert "gross" in first_row.columns
        assert "net" in first_row.columns
        assert "180.0" in first_row.values

    def test_fail_common_none_source(self):
        """
        <summary>
        Проверка выброса исключения argument_exception при передаче None
        </summary>
        """
        # Подготовка и Действие и Проверка
        with pytest.raises(argument_exception):
            common.get_fields(None)

        with pytest.raises(argument_exception):
            common.get_entity_header(None)

        with pytest.raises(argument_exception):
            common.get_entity_table(None)
