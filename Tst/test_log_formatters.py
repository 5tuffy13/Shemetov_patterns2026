import datetime
import json
import sys
from pathlib import Path
import pytest

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Core.event_type_enum import event_type_enum
from Src.Core.exception import argument_exception
from Src.Core.log_level_enum import log_level_enum
from Src.Dtos.log_format_enum import log_format_enum
from Src.Logics.csv_log_formatter import csv_log_formatter
from Src.Logics.json_log_formatter import json_log_formatter
from Src.Logics.log_formatter_factory import log_formatter_factory
from Src.Logics.markdown_log_formatter import markdown_log_formatter
from Src.Logics.text_log_formatter import text_log_formatter
from Src.Models.log_entry_model import log_entry_model


class test_log_formatters:
    """
    Модульные тесты фабрики и форматтеров экспорта журнала событий
    """

    @pytest.fixture(autouse=True)
    def setup_entries(self):
        # Подготовка
        self.factory = log_formatter_factory()
        self.entries = [
            log_entry_model(
                subsystem="storage_manager",
                level=log_level_enum.INFO,
                message="Добавлен склад | Главный",
                period=datetime.datetime(2026, 11, 26, 10, 0, 0),
                event_type=event_type_enum.ADD_ENTITY,
            ),
            log_entry_model(
                subsystem="warehouse",
                level=log_level_enum.ERROR,
                message="Ошибка построения ОСВ",
                period=datetime.datetime(2026, 11, 26, 11, 0, 0),
                event_type=event_type_enum.OSV_ERROR,
            ),
        ]

    def test_success_log_formatter_factory_creates_all_formats(self):
        """
        <summary>
        Проверка создания всех поддерживаемых форматтеров через табличную фабрику
        </summary>
        """
        # Подготовка и Действие
        fmt_json = self.factory.create(log_format_enum.JSON)
        fmt_txt = self.factory.create("TXT")
        fmt_csv = self.factory.create("csv")
        fmt_md = self.factory.create("md")

        # Проверка
        assert isinstance(fmt_json, json_log_formatter)
        assert isinstance(fmt_txt, text_log_formatter)
        assert isinstance(fmt_csv, csv_log_formatter)
        assert isinstance(fmt_md, markdown_log_formatter)

    def test_fail_log_formatter_factory_unknown_format(self):
        """
        <summary>
        Проверка выброса argument_exception при запросе неподдерживаемого формата экспорта
        </summary>
        """
        # Подготовка и Действие и Проверка
        with pytest.raises(argument_exception):
            self.factory.create("XLSX")

    def test_success_txt_formatter_attachment_response(self):
        """
        <summary>
        Проверка формирования HTTP-ответа TXT с заголовком attachment и строковым содержимым
        </summary>
        """
        # Подготовка
        formatter = self.factory.create(log_format_enum.TXT)

        # Действие
        response = formatter.create_response(self.entries, "logs")
        body = response.get_data(as_text=True)

        # Проверка
        assert "text/plain" in response.mimetype
        assert response.headers.get("Content-Disposition") == 'attachment; filename="logs.txt"'
        assert "2026-11-26T10:00:00 | storage_manager | INFO | Добавлен склад | Главный" in body
        assert "warehouse | ERROR | Ошибка построения ОСВ" in body

    def test_success_csv_formatter_attachment_response(self):
        """
        <summary>
        Проверка формирования HTTP-ответа CSV с UTF-8 BOM, разделителем ';' и вложением
        </summary>
        """
        # Подготовка
        formatter = self.factory.create(log_format_enum.CSV)

        # Действие
        response = formatter.create_response(self.entries, "logs")
        raw_bytes = response.get_data()
        body = raw_bytes.decode("utf-8-sig")

        # Проверка
        assert "text/csv" in response.mimetype
        assert response.headers.get("Content-Disposition") == 'attachment; filename="logs.csv"'
        assert raw_bytes.startswith(b"\xef\xbb\xbf")
        assert "Период;Подсистема;Уровень;Тип события;Сообщение" in body
        assert ";storage_manager;INFO;add_entity;" in body

    def test_success_markdown_formatter_inline_response(self):
        """
        <summary>
        Проверка формирования inline-ответа Markdown без заголовка attachment и с таблицей
        </summary>
        """
        # Подготовка
        formatter = self.factory.create(log_format_enum.MARKDOWN)

        # Действие
        response = formatter.create_response(self.entries, "logs")
        body = response.get_data(as_text=True)

        # Проверка
        assert "text/markdown" in response.mimetype
        assert "Content-Disposition" not in response.headers
        assert "# Журнал событий" in body
        assert "| Период | Подсистема | Уровень | Сообщение |" in body
        assert "Добавлен склад \\| Главный" in body

    def test_success_json_formatter_response(self):
        """
        <summary>
        Проверка формирования JSON-ответа с массивом сериализованных записей журнала
        </summary>
        """
        # Подготовка
        formatter = self.factory.create(log_format_enum.JSON)

        # Действие
        response = formatter.create_response(self.entries, "logs")
        data = json.loads(response.get_data(as_text=True))

        # Проверка
        assert "application/json" in response.mimetype
        assert "Content-Disposition" not in response.headers
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["subsystem"] == "storage_manager"
        assert data[1]["level"] == "ERROR"
