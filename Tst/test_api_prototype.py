import pytest
from main import app
from Src.Logics.storage_manager import storage_manager


class test_api_prototype:
    """
    Интеграционные тесты REST API фильтрации через Прототип и получения ОСВ
    """

    @pytest.fixture(autouse=True)
    def setup_client(self):
        app.testing = True
        self.client = app.test_client()
        self.storage = storage_manager()
        self.storage.clear()
        self.storage.first_start()

    def test_api_post_filter_domain_success(self):
        """
        Проверка эндпоинта POST /api/filter/{domain} для номенклатуры
        """
        # Arrange
        filter_payload = {
            "items": [
                {
                    "field_name": "name",
                    "filter_type": "LIKE",
                    "value": "мука"
                }
            ]
        }

        # Act
        response = self.client.post("/api/filter/nomenclature", json=filter_payload)

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any("мука" in item.get("name", "").lower() for item in data)

    def test_api_post_filter_domain_not_found(self):
        """
        Проверка возврата ошибки 404 при запросе неизвестной категории
        """
        response = self.client.post("/api/filter/unknown_category", json={})
        assert response.status_code == 404

    def test_api_post_osv_filter_success(self):
        """
        Проверка эндпоинта POST /api/osv/filter без условий (полная ведомость)
        """
        # Act
        response = self.client.post("/api/osv/filter", json={})

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) > 0
        first_row = data[0]
        assert "storage_name" in first_row
        assert "nomenclature_name" in first_row
        assert "start_balance" in first_row
        assert "income" in first_row
        assert "outcome" in first_row
        assert "end_balance" in first_row

    def test_api_post_osv_filter_by_nomenclature(self):
        """
        Проверка эндпоинта POST /api/osv/filter с фильтрацией по номенклатуре
        """
        # Arrange
        filter_payload = {
            "items": [
                {
                    "field_name": "nomenclature.name",
                    "filter_type": "LIKE",
                    "value": "сахар"
                }
            ]
        }

        # Act
        response = self.client.post("/api/osv/filter", json=filter_payload)

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert "сахар" in data[0]["nomenclature_name"].lower()
        assert data[0]["end_balance"] == 15000.0
