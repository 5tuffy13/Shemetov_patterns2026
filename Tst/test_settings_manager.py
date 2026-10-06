import time
import pytest
from pathlib import Path
from Src.Logics.settings_manager import settings_manager
from Src.Core.validator import operation_exception, argument_exception
from Src.Models.settings_model import settings_model


def test_not_raise_settings_manager_load():
    """
    Проверка успешной загрузки настроек по умолчанию без исключений
    """
    # Подготовка
    manager = settings_manager()

    # Действие и Проверка
    try:
        manager.load()
        assert True
    except operation_exception:
        assert False
    except Exception:
        assert False


def test_not_empty_settings_manager_load():
    """
    Проверка, что настройки после загрузки не являются пустыми
    """
    # Подготовка
    manager = settings_manager()

    # Действие
    manager.load()

    # Проверка
    assert manager.settings is not None
    assert manager.settings.company is not None
    assert manager.settings.company.name != ""


def test_equals_settings_manager_create():
    """
    Проверка работы шаблона Singleton для settings_manager
    """
    # Подготовка и Действие
    instance1 = settings_manager()
    time.sleep(0.01)
    instance2 = settings_manager()

    # Проверка
    assert instance1 is instance2


def test_equals_properties_settings_manager_create():
    """
    Проверка эквивалентности свойств синглтона settings_manager
    """
    # Подготовка и Действие
    instance1 = settings_manager()
    time.sleep(0.01)
    instance2 = settings_manager()

    # Проверка
    assert instance1.settings == instance2.settings


def test_is_loaded_settings_manager_true():
    """
    Проверка флага is_loaded после успешной загрузки
    """
    # Подготовка
    manager = settings_manager()

    # Действие
    manager.load()

    # Проверка
    assert manager.is_loaded is True


def test_fail_settings_manager_file_not_found():
    """
    Проверка выброса operation_exception при загрузке несуществующего файла
    """
    # Подготовка
    manager = settings_manager()

    # Действие и Проверка
    with pytest.raises(operation_exception):
        manager.load("non_existent_file_12345.json")


def test_fail_settings_manager_invalid_filename_type():
    """
    Проверка выброса argument_exception при некорректном типе имени файла
    """
    # Подготовка
    manager = settings_manager()

    # Действие и Проверка
    with pytest.raises(argument_exception):
        manager.load(12345)


def test_success_settings_manager_data_values(tmp_path):
    """
    Проверка корректности распарсенных значений из JSON-файла
    """
    # Подготовка
    test_json = tmp_path / "custom_settings.json"
    test_json.write_text("""{
        "company": {
            "name": "Тестовая компания",
            "inn": "1234567890",
            "bik": "123456789",
            "account": "12345678901",
            "ownership_form": "ЗАО"
        },
        "boss_name": "Петров Пётр",
        "account_name": "Сидорова Анна",
        "is_first_start": true
    }""", encoding="utf-8")
    manager = settings_manager()

    # Действие
    manager.load(str(test_json))

    # Проверка
    assert manager.is_loaded is True
    assert manager.settings.company.name == "Тестовая компания"
    assert manager.settings.company.inn == "1234567890"
    assert manager.settings.company.bik == "123456789"
    assert manager.settings.company.account == "12345678901"
    assert manager.settings.company.ownership_form == "ЗАО"
    assert manager.settings.boss_name == "Петров Пётр"
    assert manager.settings.account_name == "Сидорова Анна"
    assert manager.settings.is_first_start is True
