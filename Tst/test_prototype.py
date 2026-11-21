import pytest
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_item_dto import filter_item_dto
from Src.Dtos.filter_type_enum import filter_type_enum
from Src.Logics.prototype import prototype
from Src.Logics.storage_manager import storage_manager
from Src.Models.range_model import range_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.nomenclature_group_model import nomenclature_group_model


class test_prototype:
    """
    Модульные тесты универсального паттерна Прототип для фильтрации и клонирования
    """

    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.storage = storage_manager()
        self.storage.clear()
        self.storage.first_start()

    def test_contains_data_prototype(self):
        """
        Проверка фильтрации коллекции через прототип
        """
        # Arrange
        filter_obj = filter_dto()
        item = filter_item_dto()
        item.field_name = "name"
        item.filter_type = filter_type_enum.LIKE
        item.value = "мука"
        filter_obj.filters = [item]

        nomenclatures = self.storage.get_all(self.storage.nomenclature_key())
        pr = prototype(nomenclatures)

        # Act
        result = pr.clone(filter_obj)

        # Assert
        assert len(result.data) > 0
        assert any("мука" in x.name.lower() for x in result.data)

    def test_immutability_of_prototype(self):
        """
        Проверка гарантии неизменности исходного прототипа при клонировании
        """
        # Arrange
        nomenclatures = self.storage.get_all(self.storage.nomenclature_key())
        initial_count = len(nomenclatures)
        pr = prototype(nomenclatures)

        filter_obj = filter_dto([filter_item_dto("name", filter_type_enum.EQUALS, "Сахар")])

        # Act
        clone_pr = pr.clone(filter_obj)

        # Assert
        assert len(pr.data) == initial_count
        assert len(clone_pr.data) == 1
        assert clone_pr.data[0].name == "Сахар"

    def test_universal_prototype_multiple_domains(self):
        """
        Проверка работы единого универсального прототипа на разных типах моделей
        """
        # 1. Проверка на единицах измерения
        ranges = self.storage.get_all(self.storage.range_key())
        pr_range = prototype(ranges)
        res_range = pr_range.clone(filter_dto([filter_item_dto("name", filter_type_enum.EQUALS, "грамм")]))
        assert len(res_range.data) == 1
        assert res_range.data[0].name == "грамм"

        # 2. Проверка на складах
        storages = self.storage.get_all(self.storage.storage_key())
        pr_storage = prototype(storages)
        res_storage = pr_storage.clone(filter_dto([filter_item_dto("name", filter_type_enum.LIKE, "главный")]))
        assert len(res_storage.data) == 1
        assert "главный" in res_storage.data[0].name.lower()

    def test_nested_field_filtering(self):
        """
        Проверка фильтрации по вложенным полям и связям (требование № 4)
        """
        # Arrange: фильтруем номенклатуру по наименованию группы через точечную нотацию
        nomenclatures = self.storage.get_all(self.storage.nomenclature_key())
        pr = prototype(nomenclatures)

        filter_obj = filter_dto([filter_item_dto("group.name", filter_type_enum.EQUALS, "Молочная продукция")])

        # Act
        result = pr.clone(filter_obj)

        # Assert
        assert len(result.data) > 0
        for item in result.data:
            assert item.group.name == "Молочная продукция"

    def test_nested_base_range_filtering(self):
        """
        Проверка поиска по базовой единице измерения
        """
        # Arrange
        ranges = self.storage.get_all(self.storage.range_key())
        pr = prototype(ranges)

        filter_obj = filter_dto([filter_item_dto("base_range.name", filter_type_enum.EQUALS, "грамм")])

        # Act
        result = pr.clone(filter_obj)

        # Assert
        names = [x.name for x in result.data]
        assert "килограмм" in names
        assert "грамм" in names
