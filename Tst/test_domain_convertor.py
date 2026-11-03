import sys
import pytest
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Logics.convert_factory import convert_factory
from Src.Logics.domain_convertor import domain_convertor
from Src.Logics.mapping_factory import mapping_factory
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_row_model import receipt_row_model


class test_domain_convertor:
    """
    Тестирование конвертера доменных сущностей через DTO
    """

    @pytest.fixture(autouse=True)
    def setup_data(self):
        # Подготовка
        self.cn_factory = convert_factory()
        self.mp_factory = mapping_factory()
        self.conv = domain_convertor(self.cn_factory, self.mp_factory)
        self.unit_g = range_model("грамм", 1)
        self.unit_kg = range_model("килограмм", 1000, self.unit_g)
        self.group = nomenclature_group_model("Сырье")
        self.flour = nomenclature_model("Мука", "Мука пшеничная", self.group, self.unit_g)
        self.receipt = receipt_model("Тесто", portions=1, cooking_time=30)
        self.receipt.add_row(receipt_row_model(self.flour, gross=180.0, net=180.0))

    def test_success_domain_convertor_range_model(self):
        """
        <summary>
        Проверка преобразования единицы измерения в плоский словарь без циклических ссылок
        </summary>
        """
        # Действие
        dict_kg = self.conv.convert(self.unit_kg)

        # Проверка
        assert isinstance(dict_kg, dict)
        assert dict_kg["name"] == "килограмм"
        assert dict_kg["coeff"] == 1000
        assert dict_kg["base_code"] == self.unit_g.id

    def test_success_domain_convertor_nomenclature_model(self):
        """
        <summary>
        Проверка преобразования номенклатуры в словарь со строковыми кодами связей
        </summary>
        """
        # Действие
        dict_nom = self.conv.convert(self.flour)

        # Проверка
        assert isinstance(dict_nom, dict)
        assert dict_nom["name"] == "Мука"
        assert dict_nom["full_name"] == "Мука пшеничная"
        assert dict_nom["group_code"] == self.group.id
        assert dict_nom["range_code"] == self.unit_g.id

    def test_success_domain_convertor_receipt_model(self):
        """
        <summary>
        Проверка сериализации технологической карты с вложенным списком строк
        </summary>
        """
        # Действие
        dict_receipt = self.conv.convert(self.receipt)

        # Проверка
        assert isinstance(dict_receipt, dict)
        assert dict_receipt["name"] == "Тесто"
        assert len(dict_receipt["rows"]) == 1
        assert dict_receipt["rows"][0]["nomenclature_code"] == self.flour.id
        assert dict_receipt["rows"][0]["gross"] == 180.0

    def test_success_domain_convertor_serialize_method(self):
        """
        <summary>
        Проверка сериализации под именованным ключом через метод serialize
        </summary>
        """
        # Действие
        result = self.conv.serialize("data", self.unit_g)

        # Проверка
        assert "data" in result
        assert result["data"]["name"] == "грамм"
        assert result["data"]["coeff"] == 1
