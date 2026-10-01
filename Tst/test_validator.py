"""
Модульные тесты для класса validator
"""

import pytest
from Src.Core.validator import validator
from Src.Core.exception import argument_exception


def test_success_validator_standard_types():
    """
    <summary>
    Проверка успешной валидации стандартных типов (str, int, float, list).
    Ожидается: метод validate возвращает True.
    </summary>
    """
    assert validator.validate("Привет", str) is True
    assert validator.validate(12345, int) is True
    assert validator.validate(12.34, float) is True
    assert validator.validate([1, 2, 3], list) is True


def test_success_validator_with_max_length():
    """
    <summary>
    Проверка валидации строки с ограничением максимальной длины.
    Ожидается: True при длине строки меньше или равной max_len.
    </summary>
    """
    assert validator.validate("test", str, 4) is True
    assert validator.validate("test", str, 10) is True
    assert validator.validate(12345, int, 5) is True


def test_fail_validator_none_value():
    """
    <summary>
    Проверка выброса исключения при передаче None.
    Ожидается: argument_exception с сообщением "Пустой аргумент".
    </summary>
    """
    with pytest.raises(argument_exception) as exc:
        validator.validate(None, str)
    assert "Пустой аргумент" in exc.value.message


def test_fail_validator_invalid_type():
    """
    <summary>
    Проверка выброса исключения при несовпадении типов.
    Ожидается: argument_exception с описанием ожидаемого и полученного типа.
    </summary>
    """
    with pytest.raises(argument_exception) as exc:
        validator.validate("не число", int)
    assert "Некорректный тип" in exc.value.message


def test_fail_validator_bool_as_int_guard():
    """
    <summary>
    Проверка строгой защиты от приведения bool к int (isinstance(True, int) == True).
    Ожидается: argument_exception при передаче True или False там, где ожидается int.
    </summary>
    """
    with pytest.raises(argument_exception) as exc:
        validator.validate(True, int)
    assert "Некорректный тип" in exc.value.message

    with pytest.raises(argument_exception) as exc:
        validator.validate(False, int)
    assert "Некорректный тип" in exc.value.message


def test_fail_validator_empty_string():
    """
    <summary>
    Проверка выброса исключения для пустой строки или строки из одних пробелов.
    Ожидается: argument_exception с сообщением "Пустой аргумент".
    </summary>
    """
    with pytest.raises(argument_exception) as exc:
        validator.validate("", str)
    assert "Пустой аргумент" in exc.value.message

    with pytest.raises(argument_exception) as exc:
        validator.validate("    ", str)
    assert "Пустой аргумент" in exc.value.message


def test_fail_validator_exceeded_length():
    """
    <summary>
    Проверка выброса исключения при превышении максимальной длины строки или числа.
    Ожидается: argument_exception при длине больше len_.
    </summary>
    """
    with pytest.raises(argument_exception) as exc:
        validator.validate("слишком длинно", str, 5)
    assert "Некорректная длина аргумента" in exc.value.message

    with pytest.raises(argument_exception) as exc:
        validator.validate(1234567, int, 5)
    assert "Некорректная длина аргумента" in exc.value.message


def test_success_validator_field_name_propagation():
    """
    <summary>
    Проверка сохранения имени поля в объекте исключения argument_exception.
    Ожидается: поле exc.value.field совпадает с переданным field_name.
    </summary>
    """
    with pytest.raises(argument_exception) as exc:
        validator.validate("", str, field_name="user_name")
    assert exc.value.field == "user_name"


def test_success_validator_validate_string_method():
    """
    <summary>
    Проверка расширенного метода validate_string с минимальной и максимальной длиной.
    Ожидается: True при валидной строке, argument_exception при выходе за границы.
    </summary>
    """
    assert validator.validate_string("нормальная строка", min_len=3, max_len=50) is True

    with pytest.raises(argument_exception):
        validator.validate_string("коротко", min_len=10)

    with pytest.raises(argument_exception):
        validator.validate_string("очень длинная строка", max_len=5)

    assert validator.validate_string("", allow_empty=True) is True


def test_success_validator_validate_number_method():
    """
    <summary>
    Проверка расширенного метода validate_number для чисел и диапазонов.
    Ожидается: True при корректных значениях, argument_exception при нарушении ограничений.
    </summary>
    """
    assert validator.validate_number(10, min_value=1, max_value=100) is True
    assert validator.validate_number(5.5, positive_only=True) is True

    with pytest.raises(argument_exception):
        validator.validate_number(0, positive_only=True)

    with pytest.raises(argument_exception):
        validator.validate_number(-5, min_value=0)

    with pytest.raises(argument_exception):
        validator.validate_number(150, max_value=100)


def test_success_validator_validate_digits_method():
    """
    <summary>
    Проверка расширенного метода validate_digits для банковских и налоговых реквизитов.
    Ожидается: True для строк из цифр указанной длины, argument_exception при буквах или неверной длине.
    </summary>
    """
    # ИНН (10 или 12 цифр)
    assert validator.validate_digits("1234567890", allowed_lengths=(10, 12)) is True
    assert validator.validate_digits("123456789012", allowed_lengths=(10, 12)) is True

    # БИК (9 цифр)
    assert validator.validate_digits("123456789", length=9) is True

    # Счет (11 цифр)
    assert validator.validate_digits("12345678901", length=11) is True

    # Ошибки: буквы или пробелы
    with pytest.raises(argument_exception):
        validator.validate_digits("12345abc90", length=10)

    with pytest.raises(argument_exception):
        validator.validate_digits("12345", length=10)
