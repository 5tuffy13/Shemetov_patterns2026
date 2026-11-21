import pytest
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_item_dto import filter_item_dto
from Src.Dtos.filter_type_enum import filter_type_enum
from Src.Logics.osv_service import osv_service
from Src.Logics.storage_manager import storage_manager


class test_osv_service:
    """
    Модульные тесты сервиса Оборотно-сальдовой ведомости (ОСВ)
    """

    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.storage = storage_manager()
        self.storage.clear()
        self.storage.first_start()
        self.service = osv_service(self.storage)

    def test_success_osv_calculation_without_filters(self):
        """
        Проверка формирования ОСВ по всем транзакциям хранилища
        """
        # Act
        rows = self.service.build()

        # Assert
        assert len(rows) > 0
        flour_row = next((r for r in rows if "мука" in r.nomenclature_name.lower()), None)
        assert flour_row is not None
        assert flour_row.income == 50000.0
        assert flour_row.outcome == 12000.0
        assert flour_row.end_balance == 38000.0

    def test_success_osv_with_domain_filter(self):
        """
        Проверка формирования ОСВ с фильтрацией по номенклатуре через Прототип
        """
        # Arrange
        filter_obj = filter_dto([filter_item_dto("nomenclature.name", filter_type_enum.LIKE, "сахар")])

        # Act
        rows = self.service.build(filter_obj)

        # Assert
        assert len(rows) == 1
        assert "сахар" in rows[0].nomenclature_name.lower()
        assert rows[0].income == 20000.0
        assert rows[0].outcome == 5000.0
        assert rows[0].end_balance == 15000.0

    def test_success_osv_with_date_range(self):
        """
        Проверка расчета начального сальдо и оборотов при ограничении периода
        """
        # Arrange: задаем период с 2026-11-05
        # Первая транзакция муки (приход 50000) была 2026-11-01 -> должна пойти в начальное сальдо
        # Вторая транзакция (расход 12000) была 2026-11-10 -> должна пойти в расход
        filter_obj = filter_dto([
            filter_item_dto("start_period", filter_type_enum.EQUALS, "2026-11-05"),
            filter_item_dto("nomenclature.name", filter_type_enum.LIKE, "мука"),
        ])

        # Act
        rows = self.service.build(filter_obj)

        # Assert
        assert len(rows) == 1
        row = rows[0]
        assert row.start_balance == 50000.0
        assert row.income == 0.0
        assert row.outcome == 12000.0
        assert row.end_balance == 38000.0
