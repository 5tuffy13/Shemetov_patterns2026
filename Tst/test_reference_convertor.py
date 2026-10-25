import sys
import pytest
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Core.exception import argument_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.reference_convertor import reference_convertor
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_row_model import receipt_row_model


class test_reference_convertor:
    """
    Тестирование конвертера доменных сущностей
    """

    @pytest.fixture(autouse=True)
    def setup_data(self):
        # Подготовка
        self.factory = convert_factory()
        self.conv = reference_convertor(factory=self.factory)
        self.group = nomenclature_group_model("Сырье")
        self.unit_g = range_model("грамм", 1)
        self.flour = nomenclature_model("Мука", "Мука пшеничная", self.group, self.unit_g)
        self.receipt = receipt_model("Тесто", portions=1, cooking_time=30)
        self.receipt.add_row(receipt_row_model(self.flour, gross=180.0, net=180.0))

    def test_success_reference_convertor_simple_model(self):
        """
        <summary>
        Проверка преобразования модели единицы измерения в словарь свойств
        </summary>
        """
        # Действие
        res = self.conv.convert(self.unit_g)

        # Проверка
        assert isinstance(res, dict)
        assert res["name"] == "грамм"
        assert res["coeff"] == 1
        assert "id" in res

    def test_success_reference_convertor_nested_model(self):
        """
        <summary>
        Проверка преобразования модели с вложенными связанными сущностями
        </summary>
        """
        # Действие
        res = self.conv.convert(self.flour)

        # Проверка
        assert isinstance(res, dict)
        assert res["name"] == "Мука"
        assert res["full_name"] == "Мука пшеничная"
        assert isinstance(res["group"], dict)
        assert res["group"]["name"] == "Сырье"
        assert isinstance(res["range"], dict)
        assert res["range"]["name"] == "грамм"

    def test_success_reference_convertor_aggregate_with_rows(self):
        """
        <summary>
        Проверка преобразования агрегата технологической карты со строками
        </summary>
        """
        # Действие
        res = self.conv.convert(self.receipt)

        # Проверка
        assert isinstance(res, dict)
        assert res["name"] == "Тесто"
        assert res["gross"] == 180.0
        assert isinstance(res["rows"], list)
        assert len(res["rows"]) == 1
        assert res["rows"][0]["name"] == "Мука"

    def test_fail_reference_convertor_none_or_invalid_type(self):
        """
        <summary>
        Проверка валидации входных аргументов конвертера сущностей
        </summary>
        """
        # Действие и Проверка
        with pytest.raises(argument_exception):
            self.conv.convert(None)

        with pytest.raises(argument_exception):
            self.conv.convert("строка")
