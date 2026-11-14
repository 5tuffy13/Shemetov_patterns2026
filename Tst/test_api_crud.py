import sys
import json
import pytest
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from main import app
from Src.Logics.storage_manager import storage_manager
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model


class test_api_crud:
    """
    Интеграционные тесты CRUD-операций REST API и контроля ссылочной целостности
    """

    @pytest.fixture(autouse=True)
    def setup_client(self):
        app.testing = True
        self.client = app.test_client()
        self.storage = storage_manager()
        self.storage.clear()
        self.storage.first_start()

    def test_success_get_reports_formats_json(self):
        """
        Проверка эндпоинта /api/reports/formats: получение форматов в JSON
        """
        # Arrange & Act
        response = self.client.get("/api/reports/formats")

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert "CSV" in data
        assert "MARKDOWN" in data
        assert "HTML" in data
        assert "XML" in data

    def test_success_crud_storage_lifecycle(self):
        """
        Проверка полного жизненного цикла CRUD для склада
        """
        # 1. POST: Создание
        new_storage_data = {
            "name": "Новый распределительный центр",
            "address": "г. Красноярск, ул. Северная, д. 12"
        }
        res_post = self.client.post("/api/entities/storage", json=new_storage_data)
        assert res_post.status_code == 201
        created = res_post.get_json()
        assert created["name"] == new_storage_data["name"]
        storage_id = created["id"]

        # 2. GET by ID
        res_get = self.client.get(f"/api/entities/storage/{storage_id}")
        assert res_get.status_code == 200
        assert res_get.get_json()["address"] == new_storage_data["address"]

        # 3. PUT: Обновление
        update_data = {
            "id": storage_id,
            "name": "Обновленный распределительный центр",
            "address": "г. Красноярск, ул. Южная, д. 99"
        }
        res_put = self.client.put(f"/api/entities/storage/{storage_id}", json=update_data)
        assert res_put.status_code == 200
        assert res_put.get_json()["name"] == update_data["name"]

        # 4. DELETE: Удаление
        res_del = self.client.delete(f"/api/entities/storage/{storage_id}")
        assert res_del.status_code == 200

        # 5. GET after DELETE -> 404
        res_check = self.client.get(f"/api/entities/storage/{storage_id}")
        assert res_check.status_code == 404

    def test_success_crud_range_lifecycle(self):
        """
        Проверка CRUD для новой единицы измерения без зависимостей
        """
        # Arrange: создаем единицу "миллиграмм" с базовой единицей "грамм"
        gram = self.storage.get_range("грамм")
        assert gram is not None

        new_range_data = {
            "name": "миллиграмм",
            "coeff": 0.001,
            "base_code": gram.id
        }

        # Act: POST
        res_post = self.client.post("/api/entities/range_model", json=new_range_data)

        # Assert
        assert res_post.status_code == 201
        created = res_post.get_json()
        assert created["name"] == "миллиграмм"
        range_id = created["id"]

        # Act & Assert: DELETE
        res_del = self.client.delete(f"/api/entities/range_model/{range_id}")
        assert res_del.status_code == 200

    def test_fail_delete_range_has_derived_unit(self):
        """
        Запрет удаления базовой единицы, если от нее зависят другие единицы
        """
        # Arrange: пытаемся удалить "грамм", от которого зависит "килограмм"
        gram = self.storage.get_range("грамм")
        assert gram is not None

        # Act
        response = self.client.delete(f"/api/entities/range_model/{gram.id}")

        # Assert
        assert response.status_code == 409
        error_msg = response.get_json().get("error", "")
        assert "используется как базовая" in error_msg

    def test_fail_delete_group_has_nomenclature(self):
        """
        Запрет удаления группы номенклатуры, к которой привязаны товары
        """
        # Arrange: пытаемся удалить группу "Сырье и бакалея"
        group = self.storage.get_group("Сырье и бакалея")
        assert group is not None

        # Act
        response = self.client.delete(f"/api/entities/group_model/{group.id}")

        # Assert
        assert response.status_code == 409
        error_msg = response.get_json().get("error", "")
        assert "используется в номенклатуре" in error_msg

    def test_fail_delete_nomenclature_in_recipe(self):
        """
        Запрет удаления номенклатуры, которая входит в состав рецепта
        """
        # Arrange: пытаемся удалить "Мука пшеничная"
        flour = self.storage.get_nomenclature("Мука пшеничная")
        assert flour is not None

        # Act
        response = self.client.delete(f"/api/entities/nomenclature_model/{flour.id}")

        # Assert
        assert response.status_code == 409
        error_msg = response.get_json().get("error", "")
        assert "используется в рецепте" in error_msg

    def test_fail_delete_recipe_in_subrecipe(self):
        """
        Запрет удаления технологической карты, которая входит как полуфабрикат в другой рецепт
        """
        # Arrange: рецепт "Тесто для пиццы" входит в состав "Пицца Пепперони"
        dough = self.storage.get_receipt("Тесто для пиццы")
        assert dough is not None

        # Act
        response = self.client.delete(f"/api/entities/receipt_model/{dough.id}")

        # Assert
        assert response.status_code == 409
        error_msg = response.get_json().get("error", "")
        assert "используется как полуфабрикат" in error_msg

    def test_fail_update_range_id_when_has_dependencies(self):
        """
        Запрет изменения ID сущности при наличии зависимостей
        """
        # Arrange
        gram = self.storage.get_range("грамм")
        assert gram is not None

        update_data = {
            "id": "new-fake-gram-id",
            "name": gram.name,
            "coeff": gram.coeff,
            "base_code": ""
        }

        # Act
        response = self.client.put(f"/api/entities/range_model/{gram.id}", json=update_data)

        # Assert
        assert response.status_code == 409
        error_msg = response.get_json().get("error", "")
        assert "Запрещено изменять код (id)" in error_msg
