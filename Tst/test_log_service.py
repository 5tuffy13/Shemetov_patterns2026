import datetime
import sys
from pathlib import Path
import pytest

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Core.event_type_enum import event_type_enum
from Src.Core.exception import operation_exception
from Src.Core.log_level_enum import log_level_enum
from Src.Core.sort_direction_enum import sort_direction_enum
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_item_dto import filter_item_dto
from Src.Dtos.filter_type_enum import filter_type_enum
from Src.Dtos.log_query_dto import log_query_dto
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.log_service import log_service
from Src.Logics.observer import observer
from Src.Logics.osv_service import osv_service
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model
from Src.Models.storage_model import storage_model
from Src.Models.transaction_model import transaction_model


class test_log_service:
    """
    Модульные тесты сервиса журналирования, интеграции с менеджерами, фильтрации и сортировки
    """

    @pytest.fixture(autouse=True)
    def setup_service(self):
        # Подготовка
        self.log_svc = log_service()
        self.log_svc.ensure_subscribed()
        self.log_svc.clear()
        self.storage = storage_manager()
        self.storage.clear()
        yield
        self.storage.clear()
        self.log_svc.clear()

    def test_success_log_service_captures_settings_events(self):
        """
        <summary>
        Проверка фиксации событий загрузки, изменения и ошибки настроек в settings_manager
        </summary>
        """
        # Подготовка
        mgr = settings_manager()
        new_settings = settings_model()
        new_settings.response_format = report_type_enum.CSV

        # Действие
        mgr.load()
        mgr.update_settings(new_settings)
        with pytest.raises(operation_exception):
            mgr.load("missing_settings_test_file.json")

        # Проверка
        entries = self.log_svc.get_all()
        event_types = [entry.event_type for entry in entries]
        assert event_type_enum.LOAD_SETTINGS in event_types
        assert event_type_enum.CHANGE_SETTINGS in event_types
        assert event_type_enum.SETTINGS_ERROR in event_types

        error_entries = [e for e in entries if e.event_type == event_type_enum.SETTINGS_ERROR]
        assert error_entries[0].level == log_level_enum.ERROR
        assert error_entries[0].subsystem == "settings_manager"

    def test_success_log_service_captures_storage_crud_events(self):
        """
        <summary>
        Проверка фиксации операций CRUD, складской транзакции и ошибки удаления в storage_manager
        </summary>
        """
        # Подготовка
        self.storage.first_start()
        new_storage = storage_model("Резервный склад", "г. Красноярск, ул. Мира, 10")
        updated_storage = storage_model("Резервный склад обновленный", "г. Красноярск, ул. Мира, 20")
        updated_storage.id = new_storage.id

        nom = self.storage.nomenclatures[0]
        unit = self.storage.ranges[0]
        tx = transaction_model("Дополнительный приход", self.storage.storages[0], nom, unit, 500.0)

        # Действие
        self.storage.add(self.storage.storage_key(), new_storage)
        self.storage.update(self.storage.storage_key(), new_storage.id, updated_storage)
        self.storage.add_transaction(tx)
        self.storage.delete(self.storage.storage_key(), new_storage.id)
        flour = self.storage.get_nomenclature("Мука пшеничная")
        with pytest.raises(operation_exception):
            self.storage.delete(self.storage.nomenclature_key(), flour.id)

        # Проверка
        entries = self.log_svc.get_all()
        event_types = [entry.event_type for entry in entries]
        assert event_type_enum.STORAGE_LOADED in event_types
        assert event_type_enum.ADD_ENTITY in event_types
        assert event_type_enum.UPDATE_ENTITY in event_types
        assert event_type_enum.TRANSACTION_CREATED in event_types
        assert event_type_enum.DELETE_ENTITY in event_types
        assert event_type_enum.STORAGE_ERROR in event_types

    def test_success_log_service_captures_osv_events(self):
        """
        <summary>
        Проверка фиксации события формирования оборотно-сальдовой ведомости сервисом osv_service
        </summary>
        """
        # Подготовка
        self.storage.first_start()
        self.log_svc.clear()
        osv_svc = osv_service(self.storage)

        # Действие
        rows = osv_svc.build()

        # Проверка
        assert len(rows) > 0
        entries = self.log_svc.get_all()
        assert len(entries) == 1
        assert entries[0].event_type == event_type_enum.OSV_BUILT
        assert entries[0].subsystem == "warehouse"
        assert entries[0].level == log_level_enum.INFO

    def test_success_log_service_filter_via_prototype(self):
        """
        <summary>
        Проверка фильтрации записей журнала по уровню, подсистеме и диапазону дат через prototype
        </summary>
        """
        # Подготовка
        t1 = datetime.datetime(2026, 11, 20, 9, 0, 0)
        t2 = datetime.datetime(2026, 11, 25, 12, 0, 0)
        t3 = datetime.datetime(2026, 11, 26, 15, 30, 0)

        observer().notify(
            event_type_enum.STORAGE_ERROR,
            {"subsystem": "storage_manager", "level": log_level_enum.ERROR, "message": "Старая ошибка", "period": t1},
        )
        observer().notify(
            event_type_enum.STORAGE_ERROR,
            {"subsystem": "storage_manager", "level": log_level_enum.ERROR, "message": "Актуальная ошибка", "period": t2},
        )
        observer().notify(
            event_type_enum.OSV_BUILT,
            {"subsystem": "warehouse", "level": log_level_enum.INFO, "message": "Успешный расчет", "period": t3},
        )

        query = log_query_dto(
            filter_obj=filter_dto([
                filter_item_dto("level", filter_type_enum.EQUALS, "ERROR"),
                filter_item_dto("subsystem", filter_type_enum.LIKE, "storage"),
                filter_item_dto("period", filter_type_enum.GREATER_OR_EQUAL, "2026-11-24T00:00:00"),
                filter_item_dto("period", filter_type_enum.LESS_OR_EQUAL, "2026-11-26T00:00:00"),
            ]),
        )

        # Действие
        result = self.log_svc.query(query)

        # Проверка
        assert len(result) == 1
        assert result[0].message == "Актуальная ошибка"
        assert result[0].level == log_level_enum.ERROR

    def test_success_log_service_sort_asc_and_desc(self):
        """
        <summary>
        Проверка сортировки записей журнала по дате, уровню и подсистеме в направлениях ASC и DESC
        </summary>
        """
        # Подготовка
        t1 = datetime.datetime(2026, 11, 26, 8, 0, 0)
        t2 = datetime.datetime(2026, 11, 26, 9, 0, 0)
        t3 = datetime.datetime(2026, 11, 26, 10, 0, 0)

        observer().notify(event_type_enum.OSV_BUILT, {"subsystem": "warehouse", "level": log_level_enum.INFO, "message": "B", "period": t2})
        observer().notify(event_type_enum.STORAGE_ERROR, {"subsystem": "alpha_sys", "level": log_level_enum.ERROR, "message": "A", "period": t1})
        observer().notify(event_type_enum.HTTP_REQUEST_STARTED, {"subsystem": "web_api", "level": log_level_enum.DEBUG, "message": "C", "period": t3})

        # Действие
        by_period_desc = self.log_svc.query(log_query_dto(sort_by="period", sort_direction=sort_direction_enum.DESC))
        by_period_asc = self.log_svc.query(log_query_dto(sort_by="period", sort_direction=sort_direction_enum.ASC))
        by_subsystem_asc = self.log_svc.query(log_query_dto(sort_by="subsystem", sort_direction=sort_direction_enum.ASC))
        by_level_asc = self.log_svc.query(log_query_dto(sort_by="level", sort_direction=sort_direction_enum.ASC))

        # Проверка
        assert [e.period for e in by_period_desc] == [t3, t2, t1]
        assert [e.period for e in by_period_asc] == [t1, t2, t3]
        assert [e.subsystem for e in by_subsystem_asc] == ["alpha_sys", "warehouse", "web_api"]
        assert [e.level.value for e in by_level_asc] == ["DEBUG", "ERROR", "INFO"]
