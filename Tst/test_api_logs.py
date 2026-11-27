import sys
from pathlib import Path
import pytest

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from main import app
from Src.Core.event_type_enum import event_type_enum
from Src.Logics.log_service import log_service
from Src.Logics.storage_manager import storage_manager


class test_api_logs:
    """
    Интеграционные тесты REST API журнала событий и HTTP-перехватчиков
    """

    @pytest.fixture(autouse=True)
    def setup_client(self):
        # Подготовка
        app.testing = True
        self.client = app.test_client()
        self.log_svc = log_service()
        self.log_svc.ensure_subscribed()
        self.log_svc.clear()
        self.storage = storage_manager()
        self.storage.clear()
        self.storage.first_start()
        yield
        self.storage.clear()
        self.log_svc.clear()

    def test_success_api_logs_get_json_and_http_hook(self):
        """
        <summary>
        Проверка возврата JSON-списка записей по GET /api/logs и фиксации HTTP-хуков
        </summary>
        """
        # Подготовка
        self.client.get("/api/entities/storage")
        self.client.post("/api/entities/storage", json={"name": "Склад Лог-Тест", "address": "ул. Тестовая, 1"})

        # Действие
        response = self.client.get("/api/logs")
        data = response.get_json()

        # Проверка
        assert response.status_code == 200
        assert "application/json" in response.content_type
        assert isinstance(data, list)
        assert len(data) > 0
        messages = [item["message"] for item in data]
        assert any("GET /api/entities/storage" in m for m in messages)
        assert any("POST /api/entities/storage" in m for m in messages)

    def test_success_api_logs_post_filter_and_sort(self):
        """
        <summary>
        Проверка фильтрации через Прототип и сортировки ASC/DESC по POST /api/logs/filter
        </summary>
        """
        # Подготовка
        self.client.get("/api/entities/unknown_entity_name")
        payload_desc = {
            "items": [
                {"field_name": "level", "filter_type": "EQUALS", "value": "ERROR"},
            ],
            "sort_by": "period",
            "sort_direction": "DESC",
        }
        payload_asc = {
            "items": [
                {"field_name": "subsystem", "filter_type": "LIKE", "value": "web_api"},
            ],
            "sort_by": "period",
            "sort_direction": "ASC",
        }

        # Действие
        res_err = self.client.post("/api/logs/filter", json=payload_desc)
        res_asc = self.client.post("/api/logs/filter", json=payload_asc)

        # Проверка
        assert res_err.status_code == 200
        err_data = res_err.get_json()
        assert len(err_data) >= 1
        assert all(item["level"] == "ERROR" for item in err_data)

        assert res_asc.status_code == 200
        asc_data = res_asc.get_json()
        assert len(asc_data) >= 2
        periods = [item["period"] for item in asc_data]
        assert periods == sorted(periods)

    def test_success_api_logs_export_txt_csv_markdown(self):
        """
        <summary>
        Проверка экспорта логов в форматах TXT, CSV и MARKDOWN через GET /api/logs/export
        </summary>
        """
        # Подготовка и Действие
        res_txt = self.client.get("/api/logs/export?format=TXT")
        res_csv = self.client.get("/api/logs/export?format=CSV")
        res_md = self.client.get("/api/logs/export?format=MARKDOWN")

        # Проверка
        assert res_txt.status_code == 200
        assert "text/plain" in res_txt.content_type
        assert res_txt.headers.get("Content-Disposition") == 'attachment; filename="logs.txt"'
        assert "storage_manager" in res_txt.get_data(as_text=True)

        assert res_csv.status_code == 200
        assert "text/csv" in res_csv.content_type
        assert res_csv.headers.get("Content-Disposition") == 'attachment; filename="logs.csv"'
        raw_csv = res_csv.get_data()
        assert raw_csv.startswith(b"\xef\xbb\xbf")
        assert "Период;Подсистема;Уровень;Тип события;Сообщение" in raw_csv.decode("utf-8-sig")

        assert res_md.status_code == 200
        assert "text/markdown" in res_md.content_type
        assert "Content-Disposition" not in res_md.headers
        md_body = res_md.get_data(as_text=True)
        assert "# Журнал событий" in md_body
        assert "| Период | Подсистема | Уровень | Сообщение |" in md_body

    def test_fail_api_logs_export_invalid_format(self):
        """
        <summary>
        Проверка возврата кода 400 при передаче некорректного формата экспорта или поля сортировки
        </summary>
        """
        # Подготовка и Действие
        res_bad_fmt = self.client.get("/api/logs/export?format=UNKNOWN")
        res_bad_sort = self.client.get("/api/logs?sort_by=unknown_field")

        # Проверка
        assert res_bad_fmt.status_code == 400
        assert res_bad_sort.status_code == 400

    def test_success_api_crud_and_osv_generate_logs(self):
        """
        <summary>
        Сквозная проверка: операции POST, PUT, DELETE и расчет ОСВ отражаются в журнале GET /api/logs
        </summary>
        """
        # Подготовка и Действие
        post_res = self.client.post(
            "/api/entities/storage",
            json={"name": "Временный склад", "address": "г. Красноярск, ул. Ленина, 77"},
        )
        assert post_res.status_code == 201
        created_id = post_res.get_json()["id"]

        put_res = self.client.put(
            f"/api/entities/storage/{created_id}",
            json={"id": created_id, "name": "Временный склад 2", "address": "г. Красноярск, ул. Ленина, 78"},
        )
        assert put_res.status_code == 200

        del_res = self.client.delete(f"/api/entities/storage/{created_id}")
        assert del_res.status_code == 200

        osv_res = self.client.post("/api/osv/filter", json={})
        assert osv_res.status_code == 200

        logs_res = self.client.get("/api/logs")
        logs_data = logs_res.get_json()

        # Проверка
        assert logs_res.status_code == 200
        subsystems = {item["subsystem"] for item in logs_data}
        event_types = {item["event_type"] for item in logs_data}
        assert "storage_manager" in subsystems
        assert "warehouse" in subsystems
        assert "web_api" in subsystems
        assert event_type_enum.ADD_ENTITY.value in event_types
        assert event_type_enum.UPDATE_ENTITY.value in event_types
        assert event_type_enum.DELETE_ENTITY.value in event_types
        assert event_type_enum.OSV_BUILT.value in event_types
        assert event_type_enum.HTTP_REQUEST_COMPLETED.value in event_types
