import json
import sys
import pytest
from datetime import datetime
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Core.exception import argument_exception
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.convert_factory import convert_factory
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.dictionary_convertor import dictionary_convertor
from Src.Logics.list_convertor import list_convertor
from Src.Logics.reference_convertor import reference_convertor
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_row_model import receipt_row_model


class test_convert_factory:
    """
    Тестирование фабрики конвертации и сериализации
    """

    @pytest.fixture(autouse=True)
    def setup_data(self):
        # Подготовка
        self.factory = convert_factory()
        self.group = nomenclature_group_model("Сырье")
        self.unit_g = range_model("грамм", 1)
        self.flour = nomenclature_model("Мука", "Мука пшеничная", self.group, self.unit_g)
        self.receipt = receipt_model("Тесто", portions=1, cooking_time=30)
        self.receipt.add_row(receipt_row_model(self.flour, gross=180.0, net=180.0))

    def test_success_convert_factory_create_by_type(self):
        """
        <summary>
        Проверка фабричного метода create для подбора конвертеров по типу данных
        </summary>
        """
        # Действие
        conv_int = self.factory.create(int)
        conv_dt = self.factory.create(datetime)
        conv_list = self.factory.create(list)
        conv_dict = self.factory.create(dict)
        conv_ref = self.factory.create(receipt_model)

        # Проверка
        assert isinstance(conv_int, basic_convertor)
        assert isinstance(conv_dt, datetime_convertor)
        assert isinstance(conv_list, list_convertor)
        assert isinstance(conv_dict, dictionary_convertor)
        assert isinstance(conv_ref, reference_convertor)

    def test_success_convert_factory_create_by_object(self):
        """
        <summary>
        Проверка фабричного метода create_by_object подбора конвертера по экземпляру объекта
        </summary>
        """
        # Действие
        conv_int = self.factory.create_by_object(100)
        conv_ref = self.factory.create_by_object(self.flour)

        # Проверка
        assert isinstance(conv_int, basic_convertor)
        assert isinstance(conv_ref, reference_convertor)

    def test_success_convert_factory_serialize_json(self):
        """
        <summary>
        Проверка сериализации агрегата в валидную строку JSON стандарта RFC 8259
        </summary>
        """
        # Действие
        json_str = self.factory.serialize(self.receipt, indent=2)

        # Проверка
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["name"] == "Тесто"
        assert len(parsed["rows"]) == 1
        assert parsed["rows"][0]["name"] == "Мука"

    def test_fail_convert_factory_invalid_target_type(self):
        """
        <summary>
        Проверка выброса исключения при передаче не-типа в фабричный метод create
        </summary>
        """
        # Действие и Проверка
        with pytest.raises(argument_exception):
            self.factory.create("не тип данных")
