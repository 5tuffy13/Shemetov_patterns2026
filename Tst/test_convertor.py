import json
import sys
import pytest
from datetime import date, datetime, time
from pathlib import Path

# Определение корня проекта
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Core.exception import argument_exception
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.convert_factory import convert_factory
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_row_model import receipt_row_model


class TestBasicConvertor:
    """
    Набор тестов для базового конвертера примитивных типов данных
    """

    def test_success_basic_convertor_numbers(self):
        """
        <summary>
        Проверка корректного преобразования целых и вещественных чисел
        </summary>
        """
        # Подготовка
        conv = basic_convertor()

        # Действие
        int_res = conv.convert(42)
        float_res = conv.convert(3.14)

        # Проверка
        assert int_res == 42
        assert float_res == 3.14

    def test_success_basic_convertor_strings_and_bools(self):
        """
        <summary>
        Проверка корректного преобразования строк и логических значений
        </summary>
        """
        # Подготовка
        conv = basic_convertor()

        # Действие
        str_res = conv.convert("Тестовая строка")
        bool_res = conv.convert(True)

        # Проверка
        assert str_res == "Тестовая строка"
        assert bool_res is True

    def test_success_basic_convertor_none(self):
        """
        <summary>
        Проверка преобразования None в None
        </summary>
        """
        # Подготовка
        conv = basic_convertor()

        # Действие
        res = conv.convert(None)

        # Проверка
        assert res is None

    def test_success_basic_convertor_dict(self):
        """
        <summary>
        Проверка преобразования словаря базовых примитивов
        </summary>
        """
        # Подготовка
        conv = basic_convertor()
        raw = {"count": 10, "label": "штука", "active": True}

        # Действие
        res = conv.convert(raw)

        # Проверка
        assert res == raw

    def test_fail_basic_convertor_unsupported_type(self):
        """
        <summary>
        Проверка выброса исключения при передаче неподдерживаемого типа
        </summary>
        """
        # Подготовка
        conv = basic_convertor()

        # Действие и Проверка
        with pytest.raises(argument_exception):
            conv.convert(datetime.now())


class TestDatetimeConvertor:
    """
    Набор тестов для конвертера дат и времени
    """

    def test_success_datetime_convertor_iso_format(self):
        """
        <summary>
        Проверка преобразования объектов datetime и date в ISO-строку
        </summary>
        """
        # Подготовка
        conv = datetime_convertor()
        dt = datetime(2026, 10, 22, 12, 30, 45)
        d = date(2026, 10, 22)

        # Действие
        dt_res = conv.convert(dt)
        d_res = conv.convert(d)

        # Проверка
        assert dt_res == "2026-10-22T12:30:45"
        assert d_res == "2026-10-22"

    def test_success_datetime_convertor_dict(self):
        """
        <summary>
        Проверка преобразования словаря с датами в строковый вид
        </summary>
        """
        # Подготовка
        conv = datetime_convertor()
        raw = {"created_at": datetime(2026, 10, 22, 10, 0, 0), "deadline": date(2026, 10, 25)}

        # Действие
        res = conv.convert(raw)

        # Проверка
        assert res["created_at"] == "2026-10-22T10:00:00"
        assert res["deadline"] == "2026-10-25"

    def test_fail_datetime_convertor_unsupported_type(self):
        """
        <summary>
        Проверка выброса исключения при передаче неподдерживаемого типа
        </summary>
        """
        # Подготовка
        conv = datetime_convertor()

        # Действие и Проверка
        with pytest.raises(argument_exception):
            conv.convert(12345)


class TestReferenceConvertor:
    """
    Набор тестов для конвертера доменных моделей
    """

    def test_success_reference_convertor_simple_entity(self):
        """
        <summary>
        Проверка преобразования простой модели (единица измерения) в словарь
        </summary>
        """
        # Подготовка
        conv = reference_convertor()
        unit = range_model("грамм", 1)

        # Действие
        res = conv.convert(unit)

        # Проверка
        assert isinstance(res, dict)
        assert res["name"] == "грамм"
        assert res["coeff"] == 1
        assert "id" in res

    def test_fail_reference_convertor_none_or_invalid_type(self):
        """
        <summary>
        Проверка валидации входных аргументов конвертера сущностей
        </summary>
        """
        # Подготовка
        conv = reference_convertor()

        # Действие и Проверка
        with pytest.raises(argument_exception):
            conv.convert(None)

        with pytest.raises(argument_exception):
            conv.convert("строка не модель")


class TestConvertFactory:
    """
    Набор тестов для фабрики конвертации и сериализации
    """

    @pytest.fixture(autouse=True)
    def setup_data(self):
        """
        Инициализация тестовых доменных данных
        """
        # Подготовка
        self.factory = convert_factory()
        self.group = nomenclature_group_model("Сырье")
        self.unit_g = range_model("грамм", 1)
        self.flour = nomenclature_model("Мука", "Мука пшеничная", self.group, self.unit_g)
        self.water = nomenclature_model("Вода", "Вода питьевая", self.group, self.unit_g)

        self.receipt = receipt_model("Тесто", portions=1, cooking_time=30)
        self.receipt.add_row(receipt_row_model(self.flour, gross=180.0, net=180.0))
        self.receipt.add_row(receipt_row_model(self.water, gross=110.0, net=110.0))

    def test_success_convert_factory_get_convertor(self):
        """
        <summary>
        Проверка фабричного метода получения специализированного конвертера по типу
        </summary>
        """
        # Подготовка и Действие
        basic = self.factory.get_convertor(int)
        dt = self.factory.get_convertor(datetime)
        ref = self.factory.get_convertor(receipt_model)

        # Проверка
        assert isinstance(basic, basic_convertor)
        assert isinstance(dt, datetime_convertor)
        assert isinstance(ref, reference_convertor)

    def test_success_convert_factory_convert_primitives(self):
        """
        <summary>
        Проверка преобразования примитивов через метод convert фабрики
        </summary>
        """
        # Подготовка и Действие
        val_int = self.factory.convert(100)
        val_str = self.factory.convert("Строка")
        val_bool = self.factory.convert(False)

        # Проверка
        assert val_int == 100
        assert val_str == "Строка"
        assert val_bool is False

    def test_success_convert_factory_convert_domain_model(self):
        """
        <summary>
        Проверка преобразования доменной модели с вложенными зависимостями
        </summary>
        """
        # Подготовка и Действие
        res = self.factory.convert(self.flour)

        # Проверка
        assert isinstance(res, dict)
        assert res["name"] == "Мука"
        assert res["full_name"] == "Мука пшеничная"
        assert isinstance(res["group"], dict)
        assert res["group"]["name"] == "Сырье"
        assert isinstance(res["range"], dict)
        assert res["range"]["name"] == "грамм"

    def test_success_convert_factory_convert_aggregate_receipt(self):
        """
        <summary>
        Проверка преобразования сложного агрегата (рецепта с коллекцией строк)
        </summary>
        """
        # Подготовка и Действие
        res = self.factory.convert(self.receipt)

        # Проверка
        assert isinstance(res, dict)
        assert res["name"] == "Тесто"
        assert res["gross"] == 290.0
        assert res["net"] == 290.0
        assert isinstance(res["rows"], list)
        assert len(res["rows"]) == 2
        assert res["rows"][0]["name"] == "Мука"
        assert res["rows"][0]["gross"] == 180.0

    def test_success_convert_factory_serialize_json(self):
        """
        <summary>
        Проверка формирования корректной строки формата JSON
        </summary>
        """
        # Подготовка и Действие
        json_str = self.factory.serialize(self.receipt, indent=2)

        # Проверка
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["name"] == "Тесто"
        assert len(parsed["rows"]) == 2
        assert parsed["rows"][0]["name"] == "Мука"

    def test_fail_convert_factory_invalid_type_to_get_convertor(self):
        """
        <summary>
        Проверка выброса исключения при передаче не-типа в get_convertor
        </summary>
        """
        # Подготовка и Действие и Проверка
        with pytest.raises(argument_exception):
            self.factory.get_convertor("не тип")
