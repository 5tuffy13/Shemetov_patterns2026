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
from Src.Logics.csv_report import csv_report
from Src.Logics.html_report import html_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.report_factory import report_factory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Logics.text_report import text_report
from Src.Logics.xml_report import xml_report
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
        dto.binary = b"binary data"

        # Проверка
        assert bytes(dto.binary) == b"binary data"
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
            dto.binary = "не список и не байты"

    # -------------------------------------------------------------------------
    # Тесты перечисления форматов (report_type_enum)
    # -------------------------------------------------------------------------

    def test_success_report_type_enum_from_string(self):
        """
        <summary>
        Проверка корректного распознавания строковых представлений форматов отчета
        </summary>
        """
        # Подготовка и Действие
        fmt_txt = report_type_enum.from_string("txt")
        fmt_csv = report_type_enum.from_string("CSV")
        fmt_md = report_type_enum.from_string("Markdown")
        fmt_xml = report_type_enum.from_string("xml")
        fmt_html = report_type_enum.from_string("Html")

        # Проверка
        assert fmt_txt == report_type_enum.TXT
        assert fmt_csv == report_type_enum.CSV
        assert fmt_md == report_type_enum.MARKDOWN
        assert fmt_xml == report_type_enum.XML
        assert fmt_html == report_type_enum.HTML

    def test_fail_report_type_enum_from_invalid_string(self):
        """
        <summary>
        Проверка выброса исключения при некорректной строке формата отчета
        </summary>
        """
        # Подготовка и Действие и Проверка
        with pytest.raises(argument_exception):
            report_type_enum.from_string("UNKNOWN_FORMAT")

    # -------------------------------------------------------------------------
    # Тесты фабрики отчетов (report_factory)
    # -------------------------------------------------------------------------

    def test_success_report_factory_create_all_types(self):
        """
        <summary>
        Проверка создания всех зарегистрированных типов отчетов через фабрику
        </summary>
        """
        # Подготовка
        factory = report_factory()

        # Действие
        rep_txt = factory.create(report_type_enum.TXT)
        rep_csv = factory.create(report_type_enum.CSV)
        rep_md = factory.create(report_type_enum.MARKDOWN)
        rep_xml = factory.create(report_type_enum.XML)
        rep_html = factory.create(report_type_enum.HTML)

        # Проверка
        assert isinstance(rep_txt, text_report)
        assert isinstance(rep_csv, csv_report)
        assert isinstance(rep_md, markdown_report)
        assert isinstance(rep_xml, xml_report)
        assert isinstance(rep_html, html_report)

    def test_success_report_factory_create_default(self):
        """
        <summary>
        Проверка метода create_default: создание отчета по формату из менеджера настроек
        </summary>
        """
        # Подготовка
        mgr = settings_manager()
        mgr.settings.response_format = report_type_enum.MARKDOWN
        factory = report_factory(mgr)

        # Действие
        default_rep = factory.create_default()

        # Проверка
        assert isinstance(default_rep, markdown_report)

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
    # Тесты конкретных построителей отчетов (TXT, CSV, Markdown, XML, HTML)
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

    def test_success_csv_report_build_binary(self):
        """
        <summary>
        Проверка формирования CSV отчета в бинарном представлении
        </summary>
        """
        # Подготовка
        report = csv_report()

        # Действие
        result = report.build(self.receipt)

        # Проверка
        assert isinstance(result, report_result_dto)
        assert len(result.binary) > 0
        csv_decoded = bytes(result.binary).decode("utf-8")
        assert "id;name;gross;net" in csv_decoded
        assert "Мука;180.0;180.0" in csv_decoded

    def test_success_markdown_report_build_binary(self):
        """
        <summary>
        Проверка формирования Markdown отчета в бинарном представлении
        </summary>
        """
        # Подготовка
        report = markdown_report()

        # Действие
        result = report.build(self.receipt)

        # Проверка
        assert isinstance(result, report_result_dto)
        assert len(result.binary) > 0
        md_decoded = bytes(result.binary).decode("utf-8")
        assert "# Технологическая карта: Тесто" in md_decoded
        assert "| Код | Наименование | Брутто (г) | Нетто (г) |" in md_decoded
        assert "Мука" in md_decoded

    def test_success_xml_report_build_text(self):
        """
        <summary>
        Проверка формирования XML отчета в текстовом представлении
        </summary>
        """
        # Подготовка
        report = xml_report()

        # Действие
        result = report.build(self.receipt)

        # Проверка
        assert isinstance(result, report_result_dto)
        assert "<receipt" in result.text
        assert "<gross_total>290.0</gross_total>" in result.text
        assert "Мука" in result.text

    def test_success_html_report_build_text(self):
        """
        <summary>
        Проверка формирования HTML отчета в текстовом представлении
        </summary>
        """
        # Подготовка
        report = html_report()

        # Действие
        result = report.build(self.receipt)

        # Проверка
        assert isinstance(result, report_result_dto)
        assert "<div class=\"report-receipt\">" in result.text
        assert "<h1>Тесто</h1>" in result.text
        assert "<table>" in result.text
        assert "Мука" in result.text

    def test_success_reports_for_nomenclature_and_range(self):
        """
        <summary>
        Проверка формирования отчетов для номенклатуры и единиц измерения
        </summary>
        """
        # Подготовка
        csv_rep = csv_report()
        xml_rep = xml_report()

        # Действие
        res_nom = csv_rep.build(self.flour)
        res_range = xml_rep.build(self.unit_g)

        # Проверка
        assert "id;name;full_name;group;range" in bytes(res_nom.binary).decode("utf-8")
        assert "<range" in res_range.text
        assert "<coeff>1" in res_range.text
