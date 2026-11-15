import pytest
from Src.Logics.storage_manager import storage_manager
from Src.Logics.reference_service import reference_service
from Src.Models.storage_model import storage_model


class test_reference_service:
    """
    Модульные тесты сервиса контроля ссылочной целостности reference_service
    """

    @pytest.fixture(autouse=True)
    def setup_storage(self):
        self.storage = storage_manager()
        self.storage.clear()
        self.storage.first_start()
        self.service = reference_service(self.storage)

    def test_success_reference_service_build_index(self):
        """
        Проверка корректного формирования индекса обратных зависимостей O(1)
        """
        # Assert
        index = self.service.dependency_index
        assert isinstance(index, dict)
        assert len(index) > 0

    def test_success_can_delete_independent_entity(self):
        """
        Проверка разрешения удаления сущности без входящих связей
        """
        # Arrange
        temp_storage = storage_model(name="Временный склад", address="ул. Тестовая, 1")
        self.storage.add("storage_key", temp_storage)
        self.service.rebuild(self.storage)

        # Act
        can_delete, reason = self.service.can_delete(temp_storage.id)

        # Assert
        assert can_delete is True
        assert reason == ""

    def test_fail_cannot_delete_referenced_base_range(self):
        """
        Проверка блокировки удаления базовой единицы измерения
        """
        # Arrange
        gram = self.storage.get_range("грамм")
        assert gram is not None

        # Act
        can_delete, reason = self.service.can_delete(gram.id)

        # Assert
        assert can_delete is False
        assert "используется как базовая" in reason

    def test_fail_cannot_delete_referenced_group(self):
        """
        Проверка блокировки удаления группы номенклатуры при наличии товаров
        """
        # Arrange
        group = self.storage.get_group("Сырье и бакалея")
        assert group is not None

        # Act
        can_delete, reason = self.service.can_delete(group.id)

        # Assert
        assert can_delete is False
        assert "используется в номенклатуре" in reason

    def test_fail_cannot_delete_referenced_nomenclature(self):
        """
        Проверка блокировки удаления номенклатуры при наличии в рецептах
        """
        # Arrange
        flour = self.storage.get_nomenclature("Мука пшеничная")
        assert flour is not None

        # Act
        can_delete, reason = self.service.can_delete(flour.id)

        # Assert
        assert can_delete is False
        assert "используется в рецепте" in reason

    def test_fail_cannot_delete_subrecipe(self):
        """
        Проверка блокировки удаления полуфабриката при вложенности в другой рецепт
        """
        # Arrange
        dough = self.storage.get_receipt("Тесто для пиццы")
        assert dough is not None

        # Act
        can_delete, reason = self.service.can_delete(dough.id)

        # Assert
        assert can_delete is False
        assert "используется как полуфабрикат" in reason
