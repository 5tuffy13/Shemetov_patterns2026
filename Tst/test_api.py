import sys
import pytest
from pathlib import Path

# Определение корня проекта
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from main import app
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager


class TestApi:
    """
    Набор тестов для REST API приложения
    """

    @pytest.fixture(autouse=True)
    def setup_client(self):
        """
        Инициализация тестового клиента Flask
        """
        # Подготовка
        app.testing = True
        self.client = app.test_client()
        self.storage = storage_manager()
        self.storage.clear()
        self.storage.first_start()
        self.settings = settings_manager()
        self.settings.settings.response_format = report_type_enum.MARKDOWN

    def test_success_get_healthcheck(self):
        """
        <summary>
        Проверка доступности базового проверочного эндпоинта /api/get_report
        </summary>
        """
        # Подготовка и Действие
        response = self.client.get("/api/get_report")

        # Проверка
        assert response.status_code == 200
        assert response.data.decode("utf-8") == "success"

    def test_success_get_report_receipt_markdown_download(self):
        """
        <summary>
        Проверка выгрузки Markdown-отчета для рецепта в виде скачиваемого файла
        </summary>
        """
        # Подготовка и Действие
        response = self.client.get("/api/report/receipt/Пицца Пепперони?format=Markdown")

        # Проверка
        assert response.status_code == 200
        assert "attachment" in response.headers.get("Content-Disposition", "")
        assert ".md" in response.headers.get("Content-Disposition", "")
        content = response.data.decode("utf-8")
        assert "# Технологическая карта: Пицца Пепперони" in content
        assert "Тесто для пиццы" in content

    def test_success_get_report_receipt_csv_download(self):
        """
        <summary>
        Проверка выгрузки CSV-отчета для рецепта в виде скачиваемого файла
        </summary>
        """
        # Подготовка и Действие
        response = self.client.get("/api/report/receipt/Пицца Пепперони?format=CSV")

        # Проверка
        assert response.status_code == 200
        assert "attachment" in response.headers.get("Content-Disposition", "")
        assert ".csv" in response.headers.get("Content-Disposition", "")
        content = response.data.decode("utf-8")
        assert "id;name;gross;net" in content

    def test_success_get_report_receipt_xml_text(self):
        """
        <summary>
        Проверка структурированного XML-ответа для технологической карты
        </summary>
        """
        # Подготовка и Действие
        response = self.client.get("/api/report/receipt/Пицца Пепперони?format=XML")

        # Проверка
        assert response.status_code == 200
        assert "application/xml" in response.headers.get("Content-Type", "")
        content = response.data.decode("utf-8")
        assert "<receipt" in content
        assert "Пицца Пепперони" in content

    def test_success_get_report_receipt_html_text(self):
        """
        <summary>
        Проверка структурированного HTML-ответа для технологической карты
        </summary>
        """
        # Подготовка и Действие
        response = self.client.get("/api/report/receipt/Пицца Пепперони?format=HTML")

        # Проверка
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        content = response.data.decode("utf-8")
        assert "<div class=\"report-receipt\">" in content
        assert "Пицца Пепперони" in content

    def test_success_get_report_nomenclature_csv_download(self):
        """
        <summary>
        Проверка выгрузки CSV-отчета для номенклатуры в виде скачиваемого файла
        </summary>
        """
        # Подготовка и Действие
        response = self.client.get("/api/report/nomenclature/Мука пшеничная?format=CSV")

        # Проверка
        assert response.status_code == 200
        assert "attachment" in response.headers.get("Content-Disposition", "")
        assert ".csv" in response.headers.get("Content-Disposition", "")
        content = response.data.decode("utf-8")
        assert "id;name;full_name;group;range" in content
        assert "Мука пшеничная" in content

    def test_success_get_report_range_xml_text(self):
        """
        <summary>
        Проверка выгрузки XML-отчета для единицы измерения
        </summary>
        """
        # Подготовка и Действие
        response = self.client.get("/api/report/range/грамм?format=XML")

        # Проверка
        assert response.status_code == 200
        assert "application/xml" in response.headers.get("Content-Type", "")
        content = response.data.decode("utf-8")
        assert "<range" in content
        assert "грамм" in content

    def test_success_get_report_default_endpoint(self):
        """
        <summary>
        Проверка эндпоинта /api/report/default/<entity_type>/<id> с форматом по умолчанию
        </summary>
        """
        # Подготовка
        self.settings.settings.response_format = report_type_enum.MARKDOWN

        # Действие
        response = self.client.get("/api/report/default/receipt/Пицца Пепперони")

        # Проверка
        assert response.status_code == 200
        assert "attachment" in response.headers.get("Content-Disposition", "")
        assert ".md" in response.headers.get("Content-Disposition", "")

    def test_fail_get_report_unknown_entity(self):
        """
        <summary>
        Проверка возврата ошибки 404 при запросе несуществующей сущности
        </summary>
        """
        # Подготовка и Действие
        response = self.client.get("/api/report/receipt/НесуществующееБлюдо")

        # Проверка
        assert response.status_code == 404

    def test_fail_get_report_invalid_format(self):
        """
        <summary>
        Проверка возврата ошибки 400 при указании некорректного формата отчета
        </summary>
        """
        # Подготовка и Действие
        response = self.client.get("/api/report/receipt/Пицца Пепперони?format=INVALID_FORMAT")

        # Проверка
        assert response.status_code == 400


    def test_success_get_entities(self):
        """
        <summary>
        Проверка эндпоинта /api/get_entities: получение списка доменных категорий
        </summary>
        """
        # Подготовка и Действие
        response = self.client.get("/api/get_entities")

        # Проверка
        assert response.status_code == 200
        content = response.data.decode("utf-8")
        assert "receipt_model" in content
        assert "nomenclature_model" in content
        assert "range_model" in content

    def test_success_get_formats(self):
        """
        <summary>
        Проверка эндпоинта /api/get_formats: получение списка форматов отчетов
        </summary>
        """
        # Подготовка и Действие
        response = self.client.get("/api/get_formats")

        # Проверка
        assert response.status_code == 200
        content = response.data.decode("utf-8")
        assert "CSV" in content
        assert "MARKDOWN" in content
        assert "TXT" in content

    def test_success_get_default_report_query_params(self):
        """
        <summary>
        Проверка эндпоинта /api/get_default_report с query-параметрами entity и unique_code
        </summary>
        """
        # Подготовка
        self.settings.settings.response_format = report_type_enum.MARKDOWN

        # Действие
        response = self.client.get("/api/get_default_report?entity=receipt_model&unique_code=Пицца Пепперони")

        # Проверка
        assert response.status_code == 200
        assert "attachment" in response.headers.get("Content-Disposition", "")
        assert ".md" in response.headers.get("Content-Disposition", "")

    def test_fail_get_default_report_missing_params(self):
        """
        <summary>
        Проверка возврата ошибки 400 при отсутствии обязательных параметров в /api/get_default_report
        </summary>
        """
        # Подготовка и Действие
        response = self.client.get("/api/get_default_report")

        # Проверка
        assert response.status_code == 400
