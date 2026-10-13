import sys
import pytest
from pathlib import Path

# Определение корня проекта
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Core.exception import argument_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.report_factory import report_factory
from Src.Logics.storage_manager import storage_manager
from Src.Logics.text_report import text_report
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_row_model import receipt_row_model


class TestReports:
    """
    Набор тестов для фабрики и построителей отчетов
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

    # -------------------------------------------------------------------------
    # Тесты DTO результата отчета (report_result_dto)
    # -------------------------------------------------------------------------

    def test_success_report_result_dto_text_property(self):
        """
        <summary>
        Проверка установки текстового содержимого и сброса бинарного буфера
        </summary>
        """
        # Подготовка
        dto = report_result_dto()

        # Действие
        dto.text = "Тестовый отчет"

        # Проверка
        assert dto.text == "Тестовый отчет"
        assert dto.binary == []

    def test_success_report_result_dto_binary_property(self):
        """
        <summary>
        Проверка установки бинарного содержимого и сброса текстового буфера
        </summary>
        """
        # Подготовка
        dto = report_result_dto(text="Исходный текст")

        # Действие
        dto.binary = [1, 2, 3, 4]

        # Проверка
        assert dto.binary == [1, 2, 3, 4]
        assert dto.text == ""

    def test_fail_report_result_dto_invalid_type(self):
        """
        <summary>
        Проверка валидации некорректных типов данных в сеттерах DTO
        </summary>
        """
        # Подготовка
        dto = report_result_dto()

        # Действие и проверка
        with pytest.raises(argument_exception):
            dto.text = 12345

        with pytest.raises(argument_exception):
            dto.binary = "не список"

    # -------------------------------------------------------------------------
    # Тесты фабрики отчетов (report_factory)
    # -------------------------------------------------------------------------

    def test_success_report_factory_create_text_report(self):
        """
        <summary>
        Проверка создания инстанса текстового отчета через фабрику
        </summary>
        """
        # Подготовка
        factory = report_factory()

        # Действие
        report = factory.create(report_type_enum.TXT)

        # Проверка
        assert isinstance(report, text_report)

    def test_fail_report_factory_invalid_argument_type(self):
        """
        <summary>
        Проверка выброса исключения при передаче некорректного типа в фабрику
        </summary>
        """
        # Подготовка
        factory = report_factory()

        # Действие и проверка
        with pytest.raises(argument_exception):
            factory.create("TXT")

    # -------------------------------------------------------------------------
    # Тесты генератора текстового отчета (text_report)
    # -------------------------------------------------------------------------

    def test_success_text_report_build(self):
        """
        <summary>
        Проверка формирования текстового отчета по технологической карте
        </summary>
        """
        # Подготовка
        report = text_report()

        # Действие
        result = report.build(self.receipt)

        # Проверка
        assert isinstance(result, report_result_dto)
        assert "Код | Наименование | Брутто | Нетто" in result.text
        assert "Мука" in result.text
        assert "Вода" in result.text
        assert "180.0" in result.text
        assert "110.0" in result.text

    def test_fail_text_report_invalid_source_type(self):
        """
        <summary>
        Проверка валидации типа источника данных при построении текстового отчета
        </summary>
        """
        # Подготовка
        report = text_report()

        # Действие и проверка
        with pytest.raises(argument_exception):
            report.build(self.flour)

    def test_success_text_report_with_pizza_seed_data(self):
        """
        <summary>
        Проверка формирования отчета по авторской пицце из хранилища данных
        </summary>
        """
        # Подготовка
        manager = storage_manager()
        manager.clear()
        manager.first_start()
        pizza = manager.get_receipt("Пицца Пепперони")

        factory = report_factory()
        report = factory.create(report_type_enum.TXT)

        # Действие
        result = report.build(pizza)

        # Проверка
        assert isinstance(result, report_result_dto)
        assert "Код | Наименование | Брутто | Нетто" in result.text
        assert "Тесто для пиццы" in result.text
        assert "Соус томатный фирменный" in result.text
        assert "Сыр Моцарелла" in result.text
        assert "Колбаски Пепперони" in result.text
