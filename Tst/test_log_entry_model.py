import datetime
import sys
from pathlib import Path
import pytest

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Core.event_type_enum import event_type_enum
from Src.Core.exception import argument_exception
from Src.Core.log_level_enum import log_level_enum
from Src.Dtos.log_entry_dto import log_entry_dto
from Src.Logics.convertor import convertor
from Src.Models.log_entry_model import log_entry_model


class test_log_entry_model:
    """
    Модульные тесты доменной модели и DTO записи журнала событий
    """

    def test_success_log_entry_model_creation(self):
        """
        <summary>
        Проверка корректной инициализации и установки полей модели записи журнала через сеттеры
        </summary>
        """
        # Подготовка
        ts = datetime.datetime(2026, 11, 26, 10, 30, 0)

        # Действие
        entry = log_entry_model(
            subsystem="storage_manager",
            level="error",
            message="Тестовая ошибка хранилища",
            period=ts,
            event_type="storage_error",
        )

        # Проверка
        assert entry.subsystem == "storage_manager"
        assert entry.level == log_level_enum.ERROR
        assert entry.message == "Тестовая ошибка хранилища"
        assert entry.period == ts
        assert entry.event_type == event_type_enum.STORAGE_ERROR
        assert entry.id != ""

    def test_fail_log_entry_model_invalid_fields(self):
        """
        <summary>
        Проверка выброса argument_exception при некорректных значениях полей записи журнала
        </summary>
        """
        # Подготовка и Действие и Проверка
        with pytest.raises(argument_exception):
            log_entry_model(subsystem="", message="Текст")

        with pytest.raises(argument_exception):
            log_entry_model(subsystem="warehouse", message="   ")

        with pytest.raises(argument_exception):
            log_entry_model(subsystem="warehouse", message="Текст", period="2026-11-26")

        with pytest.raises(argument_exception):
            log_entry_model(subsystem="warehouse", message="Текст", level="CRITICAL")

    def test_success_log_entry_dto_roundtrip(self):
        """
        <summary>
        Проверка преобразования доменной модели в DTO, словарь и обратного восстановления через convertor
        </summary>
        """
        # Подготовка
        ts = datetime.datetime(2026, 11, 26, 12, 15, 0)
        entry = log_entry_model(
            subsystem="warehouse",
            level=log_level_enum.INFO,
            message="Построена ОСВ",
            period=ts,
            event_type=event_type_enum.OSV_BUILT,
        )
        conv = convertor()

        # Действие
        dto = log_entry_dto().from_domain_model(entry)
        dto_dict = dto.to_dict()
        serialized = conv.factory.domain_convertor.convert(entry)
        restored = conv.deserialize(serialized, target_type=log_entry_model)

        # Проверка
        assert dto_dict["id"] == entry.id
        assert dto_dict["period"] == ts.isoformat()
        assert dto_dict["subsystem"] == "warehouse"
        assert dto_dict["level"] == "INFO"
        assert dto_dict["event_type"] == "osv_built"
        assert dto_dict["message"] == "Построена ОСВ"
        assert "type" in dto_dict

        assert isinstance(restored, log_entry_model)
        assert restored.id == entry.id
        assert restored.subsystem == entry.subsystem
        assert restored.level == entry.level
        assert restored.event_type == entry.event_type
        assert restored.message == entry.message
        assert restored.period == entry.period
