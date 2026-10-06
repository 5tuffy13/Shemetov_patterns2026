import pytest
from Src.Core.common import common
from Src.Core.validator import argument_exception
from Src.Models.settings_model import settings_model


def test_common_get_fields_success():
    # Подготовка
    model = settings_model()

    # Действие
    fields = common.get_fields(model)

    # Проверки
    assert isinstance(fields, list)
    assert "company" in fields
    assert "boss_name" in fields
    assert "account_name" in fields
    assert "first_start" in fields


def test_common_get_fields_is_common_filter():
    # Подготовка
    model = settings_model()

    # Действие
    fields = common.get_fields(model, is_common=True)

    # Проверки
    assert isinstance(fields, list)
    assert "boss_name" in fields
    assert "account_name" in fields


def test_common_get_fields_none_raise():
    # Подготовка
    source = None

    # Действие и Проверки
    with pytest.raises(argument_exception):
        common.get_fields(source)
