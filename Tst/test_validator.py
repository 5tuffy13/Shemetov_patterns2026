"""
Модульные тесты для класса validator: базовые сценарии и глубокий аудит краевых случаев
"""

import pytest
from typing import Any, Union
from Src.Core.validator import validator, argument_exception, operation_exception

# =========================================================================
# ТЕСТЫ СОВМЕСТИМОСТИ
# =========================================================================

def test_original_standard_types():
    assert validator.validate("Привет", str) is True
    assert validator.validate(12345, int) is True
    assert validator.validate(12.34, float) is True
    assert validator.validate([1, 2, 3], list) is True


def test_original_max_length():
    assert validator.validate("test", str, 4) is True
    assert validator.validate("test", str, 10) is True
    assert validator.validate(12345, int, 5) is True


def test_original_none_value():
    with pytest.raises(argument_exception) as exc:
        validator.validate(None, str)
    assert "Пустой аргумент" in exc.value.message


def test_original_invalid_type():
    with pytest.raises(argument_exception) as exc:
        validator.validate("не число", int)
    assert "Некорректный тип" in exc.value.message


def test_original_bool_as_int_guard():
    with pytest.raises(argument_exception) as exc:
        validator.validate(True, int)
    assert "Некорректный тип" in exc.value.message

    with pytest.raises(argument_exception) as exc:
        validator.validate(False, int)
    assert "Некорректный тип" in exc.value.message


def test_original_empty_string():
    with pytest.raises(argument_exception) as exc:
        validator.validate("", str)
    assert "Пустой аргумент" in exc.value.message

    with pytest.raises(argument_exception) as exc:
        validator.validate("    ", str)
    assert "Пустой аргумент" in exc.value.message


def test_original_exceeded_length():
    with pytest.raises(argument_exception) as exc:
        validator.validate("слишком длинно", str, 5)
    assert "Некорректная длина аргумента" in exc.value.message

    with pytest.raises(argument_exception) as exc:
        validator.validate(1234567, int, 5)
    assert "Некорректная длина аргумента" in exc.value.message


def test_original_field_name_propagation():
    with pytest.raises(argument_exception) as exc:
        validator.validate("", str, field_name="user_name")
    assert exc.value.field == "user_name"


def test_original_validate_string_method():
    assert validator.validate_string("нормальная строка", min_len=3, max_len=50) is True

    with pytest.raises(argument_exception):
        validator.validate_string("коротко", min_len=10)

    with pytest.raises(argument_exception):
        validator.validate_string("очень длинная строка", max_len=5)

    assert validator.validate_string("", allow_empty=True) is True


def test_original_validate_number_method():
    assert validator.validate_number(10, min_value=1, max_value=100) is True
    assert validator.validate_number(5.5, positive_only=True) is True

    with pytest.raises(argument_exception):
        validator.validate_number(0, positive_only=True)

    with pytest.raises(argument_exception):
        validator.validate_number(-5, min_value=0)

    with pytest.raises(argument_exception):
        validator.validate_number(150, max_value=100)


def test_original_validate_digits_method():
    assert validator.validate_digits("1234567890", allowed_lengths=(10, 12)) is True
    assert validator.validate_digits("123456789012", allowed_lengths=(10, 12)) is True
    assert validator.validate_digits("123456789", length=9) is True
    assert validator.validate_digits("12345678901", length=11) is True

    with pytest.raises(argument_exception):
        validator.validate_digits("12345abc90", length=10)

    with pytest.raises(argument_exception):
        validator.validate_digits("12345", length=10)


# =========================================================================
# ТЕСТЫ КРАЕВЫХ СЛУЧАЕВ И УСТОЙЧИВОСТИ
# =========================================================================

# 1. ЧИСЛА: NaN и Inf
def test_number_nan_fails():
    with pytest.raises(argument_exception) as exc:
        validator.validate_number(float("nan"), min_value=10, max_value=100)
    assert "NaN" in exc.value.message

    with pytest.raises(argument_exception) as exc:
        validator.validate_number(float("nan"), positive_only=True)
    assert "NaN" in exc.value.message

    with pytest.raises(argument_exception) as exc:
        validator.validate(float("nan"), float)
    assert "NaN" in exc.value.message


def test_number_inf_fails():
    with pytest.raises(argument_exception) as exc:
        validator.validate_number(float("inf"), positive_only=True)
    assert "бесконечным" in exc.value.message

    with pytest.raises(argument_exception) as exc:
        validator.validate_number(float("-inf"), min_value=-1000)
    assert "бесконечным" in exc.value.message

    with pytest.raises(argument_exception) as exc:
        validator.validate(float("inf"), float)
    assert "бесконечным" in exc.value.message


def test_number_allow_flags():
    assert validator.validate_number(float("nan"), allow_nan=True) is True
    assert validator.validate_number(float("inf"), allow_inf=True) is True


def test_number_invalid_meta_parameters():
    with pytest.raises(argument_exception) as exc:
        validator.validate_number(10, min_value=float("nan"))
    assert exc.value.field == "min_value"

    with pytest.raises(argument_exception) as exc:
        validator.validate_number(10, min_value=100, max_value=50)
    assert exc.value.field == "max_value"

    with pytest.raises(argument_exception) as exc:
        validator.validate_number(10, min_value=True)
    assert exc.value.field == "min_value"

    with pytest.raises(argument_exception) as exc:
        validator.validate_number(10, max_value=-5, positive_only=True)
    assert exc.value.field == "max_value"


# 2. ЦИФРЫ: ASCII vs Unicode и поддержка int
def test_digits_unicode_rejected():
    with pytest.raises(argument_exception) as exc:
        validator.validate_digits("¹²³", length=3)
    assert "Значение должно состоять только из цифр" in exc.value.message

    with pytest.raises(argument_exception) as exc:
        validator.validate_digits("١٢٣", length=3)
    assert "Значение должно состоять только из цифр" in exc.value.message

    with pytest.raises(argument_exception) as exc:
        validator.validate_digits("１２３", length=3)
    assert "Значение должно состоять только из цифр" in exc.value.message


def test_digits_int_support():
    assert validator.validate_digits(1234567890, length=10) is True
    assert validator.validate_digits(123456789, allowed_lengths=(9, 10)) is True

    with pytest.raises(argument_exception) as exc:
        validator.validate_digits(-12345, length=5)
    assert "отрицательным" in exc.value.message


def test_digits_bool_rejected():
    with pytest.raises(argument_exception):
        validator.validate_digits(True, length=1)


def test_digits_invalid_meta_parameters():
    with pytest.raises(argument_exception) as exc:
        validator.validate_digits("123", length=-3)
    assert exc.value.field == "length"

    with pytest.raises(argument_exception) as exc:
        validator.validate_digits("123", length=True)
    assert exc.value.field == "length"

    with pytest.raises(argument_exception) as exc:
        validator.validate_digits("123", allowed_lengths=(-1, 5))
    assert exc.value.field == "allowed_lengths"

    with pytest.raises(argument_exception) as exc:
        validator.validate_digits("123", length=5, allowed_lengths=(10, 12))
    assert exc.value.field == "length"


# 3. СТРОКИ: allow_empty vs min_len и stripped vs raw len
def test_string_allow_empty_conflict_resolved():
    assert validator.validate_string("", min_len=5, allow_empty=True) is True
    assert validator.validate_string("   ", min_len=5, allow_empty=True, strip=True) is True

    with pytest.raises(argument_exception) as exc:
        validator.validate_string("abc", min_len=5, allow_empty=True)
    assert "меньше минимальной" in exc.value.message

    with pytest.raises(argument_exception) as exc:
        validator.validate_string("", min_len=5, allow_empty=False)
    assert "Пустой аргумент" in exc.value.message


def test_string_stripped_vs_raw_len():
    assert validator.validate_string("  ab  ", min_len=2, max_len=2, strip=True) is True

    with pytest.raises(argument_exception) as exc:
        validator.validate_string("  ab  ", max_len=4, strip=False)
    assert "Некорректная длина" in exc.value.message

    assert validator.validate("  hi  ", str, len_=2, strip=True) is True
    with pytest.raises(argument_exception):
        validator.validate("  hi  ", str, len_=2, strip=False)


# 4. len_ < 0 и некорректные типы len_
def test_invalid_len_parameter():
    with pytest.raises(argument_exception) as exc:
        validator.validate("hello", str, len_=-1)
    assert exc.value.field == "len_"

    with pytest.raises(argument_exception) as exc:
        validator.validate("hello", str, len_="10")
    assert exc.value.field == "len_"

    with pytest.raises(argument_exception) as exc:
        validator.validate("hello", str, len_=True)
    assert exc.value.field == "len_"

    with pytest.raises(argument_exception) as exc:
        validator.validate_string("hello", min_len=-5)
    assert exc.value.field == "min_len"

    with pytest.raises(argument_exception) as exc:
        validator.validate_string("hello", min_len=10, max_len=5)
    assert exc.value.field == "max_len"


# 5. BOOL-AS-INT ЛОВУШКА В КОРТЕЖАХ, UNION И Т.Д.
def test_bool_as_int_nested_tuples_and_unions():
    with pytest.raises(argument_exception):
        validator.validate(True, int | float)
    with pytest.raises(argument_exception):
        validator.validate_type(False, int | float)

    with pytest.raises(argument_exception):
        validator.validate(True, Union[int, float])

    with pytest.raises(argument_exception):
        validator.validate(True, (str, (int, float)))

    with pytest.raises(argument_exception):
        validator.validate(True, (int, float))

    assert validator.validate(True, bool) is True
    assert validator.validate(True, (int, bool)) is True
    assert validator.validate(False, int | bool) is True
    assert validator.validate(True, Union[int, bool]) is True
    assert validator.validate(True, (str, (int, bool))) is True
    assert validator.validate(True, object) is True
    assert validator.validate(True, Any) is True


# 6. КОЛЛЕКЦИИ И ДОПОЛНИТЕЛЬНЫЕ ПРОВЕРКИ
def test_collection_validation():
    assert validator.validate([1, 2], list, len_=2) is True
    assert validator.validate([], list) is True
    with pytest.raises(argument_exception):
        validator.validate([1, 2, 3], list, len_=2)


def test_type_meta_errors():
    with pytest.raises(argument_exception) as exc:
        validator.validate_type("hello", None)
    assert exc.value.field == "type_"

    with pytest.raises(argument_exception) as exc:
        validator.validate_type("hello", [int])
    assert exc.value.field == "type_"
