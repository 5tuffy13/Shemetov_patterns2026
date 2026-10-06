"""
Модуль валидации данных с повышенной отказоустойчивостью и защитой от краевых случаев
"""

import math
import types
from typing import Any, Union, get_args, get_origin
from Src.Core.exception import argument_exception, operation_exception

__all__ = ["validator", "argument_exception", "operation_exception"]
class validator:
    """
    Набор проверок корректности данных с акцентом на устойчивость и краевые случаи
    """

    def __new__(cls, *args, **kwargs):
        """
        Позволяет использовать класс как вызываемую функцию: validator(val, type_, len_)
        """
        if args or kwargs:
            return cls.validate(*args, **kwargs)
        return super().__new__(cls)

    @staticmethod
    def _flatten_types(target_type: Any):
        """
        Рекурсивно разворачивает вложенные кортежи типов и объединения (Union / UnionType).
        """
        if isinstance(target_type, tuple):
            for item in target_type:
                yield from validator._flatten_types(item)
        elif isinstance(target_type, types.UnionType) or get_origin(target_type) is Union:
            for arg in get_args(target_type):
                yield from validator._flatten_types(arg)
        else:
            yield target_type

    @classmethod
    def _type_allows_bool(cls, target_type: Any) -> bool:
        """
        Проверяет, разрешен ли тип bool явно в спецификации типа target_type.
        Защита от ловушки bool-as-int в Python (issubclass(bool, int) == True).
        """
        for t in cls._flatten_types(target_type):
            if t is bool or t is object or t is Any:
                return True
        return False

    @classmethod
    def _normalize_type(cls, target_type: Any) -> Any:
        """
        Приводит спецификацию типа к форме, поддерживаемой встроенной функцией isinstance:
        - typing.Any -> object
        - параметризованные generic-типы (list[str], dict[str, Any]) -> их origin (list, dict)
        - PEP 604 Union (int | float) и typing.Union -> кортежи типов для совместимости
        """
        if target_type is Any:
            return object
        origin = get_origin(target_type)
        if origin is Union or isinstance(target_type, types.UnionType):
            args = get_args(target_type)
            return tuple(cls._normalize_type(a) for a in args)
        if origin is not None:
            return origin
        if isinstance(target_type, tuple):
            return tuple(cls._normalize_type(item) for item in target_type)
        return target_type

    @staticmethod
    def validate_type(
        value: Any,
        type_: Any,
        field_name: str = "",
    ) -> bool:
        """
        Проверка соответствия типа значения с защитой от bool-as-int.

        Args:
            value (Any): Проверяемый аргумент
            type_ (type | tuple[type, ...] | UnionType | Any): Ожидаемый тип или объединение
            field_name (str, optional): Имя поля

        Raises:
            argument_exception: Пустой аргумент, некорректный параметр типа или несовпадение типов

        Returns:
            bool: True в случае успешной валидации
        """
        if value is None:
            raise argument_exception(field_name, "Пустой аргумент")

        if type_ is None:
            raise argument_exception("type_", "Параметр типа 'type_' не может быть None!")

        # Строгая защита от bool-as-int ловушки:
        # В Python bool наследуется от int, поэтому isinstance(True, int) == True.
        # Если bool явно не указан в ожидаемых типах, логические значения отвергаются.
        if isinstance(value, bool) and not validator._type_allows_bool(type_):
            raise argument_exception(
                field_name,
                f"Некорректный тип!\nОжидается {type_}. Текущий тип {type(value)}",
            )

        norm_type = validator._normalize_type(type_)
        try:
            if not isinstance(value, norm_type):
                raise argument_exception(
                    field_name,
                    f"Некорректный тип!\nОжидается {type_}. Текущий тип {type(value)}",
                )
        except TypeError as exc:
            raise argument_exception("type_", f"Некорректная спецификация типа: {exc}")

        return True

    @staticmethod
    def validate(
        value: Any,
        type_: Any,
        len_: int | None = None,
        field_name: str = "",
        strip: bool = True,
    ) -> bool:
        """
        Валидация аргумента по типу и длине (совместимость с эталонным проектом Patterns2026).

        Args:
            value (Any): Проверяемый аргумент
            type_ (type | tuple[type, ...] | Any): Ожидаемый тип или объединение типов
            len_ (int | None, optional): Максимальная длина. По умолчанию None.
            field_name (str, optional): Имя поля. По умолчанию "".
            strip (bool, optional): Удалять ли начальные и конечные пробелы перед проверкой длины.

        Raises:
            argument_exception: Пустой аргумент, некорректный тип, некорректная длина

        Returns:
            bool: True в случае успешной валидации
        """
        validator.validate_type(value, type_, field_name=field_name)

        if len_ is not None:
            if isinstance(len_, bool) or not isinstance(len_, int):
                raise argument_exception(
                    "len_",
                    f"Параметр ограничения длины 'len_' должен быть целым числом, получено {type(len_).__name__}",
                )
            if len_ < 0:
                raise argument_exception(
                    "len_",
                    f"Параметр ограничения длины 'len_' не может быть отрицательным (получено: {len_})",
                )

        if isinstance(value, str):
            check_str = value.strip() if strip else value
            if len(check_str) == 0:
                raise argument_exception(field_name, "Пустой аргумент")
            if len_ is not None and len(check_str) > len_:
                raise argument_exception(
                    field_name,
                    f"Некорректная длина аргумента: ожидается не более {len_}",
                )
        elif isinstance(value, (int, float)):
            if isinstance(value, float):
                if math.isnan(value):
                    raise argument_exception(field_name, "Числовое значение не может быть NaN (Not a Number)!")
                if math.isinf(value):
                    raise argument_exception(field_name, "Числовое значение не может быть бесконечным (+/-Inf)!")

            str_repr = str(value).strip()
            if len(str_repr) == 0:
                raise argument_exception(field_name, "Пустой аргумент")
            if len_ is not None and len(str_repr) > len_:
                raise argument_exception(
                    field_name,
                    f"Некорректная длина аргумента: ожидается не более {len_}",
                )
        else:
            if len_ is not None:
                try:
                    if len(value) > len_:
                        raise argument_exception(
                            field_name,
                            f"Некорректная длина аргумента: ожидается не более {len_}",
                        )
                except TypeError:
                    pass

        return True

    @staticmethod
    def validate_string(
        value: Any,
        min_len: int | None = None,
        max_len: int | None = None,
        allow_empty: bool = False,
        field_name: str = "",
        strip: bool = True,
    ) -> bool:
        """
        Валидация строкового аргумента с поддержкой минимальной и максимальной длины.
        Разрешает конфликт allow_empty=True и min_len: если строка пуста и allow_empty=True,
        проверка минимальной длины игнорируется.

        Args:
            value (Any): Строковое значение
            min_len (int | None): Минимальная длина
            max_len (int | None): Максимальная длина
            allow_empty (bool): Разрешать ли пустую строку
            field_name (str): Имя поля
            strip (bool): Удалять ли начальные/конечные пробелы перед проверкой

        Returns:
            bool: True в случае успешной валидации
        """
        validator.validate_type(value, str, field_name=field_name)

        if min_len is not None:
            if isinstance(min_len, bool) or not isinstance(min_len, int):
                raise argument_exception(
                    "min_len",
                    f"Параметр 'min_len' должен быть целым числом, получено {type(min_len).__name__}",
                )
            if min_len < 0:
                raise argument_exception(
                    "min_len",
                    f"Параметр 'min_len' не может быть отрицательным (получено: {min_len})",
                )

        if max_len is not None:
            if isinstance(max_len, bool) or not isinstance(max_len, int):
                raise argument_exception(
                    "max_len",
                    f"Параметр 'max_len' должен быть целым числом, получено {type(max_len).__name__}",
                )
            if max_len < 0:
                raise argument_exception(
                    "max_len",
                    f"Параметр 'max_len' не может быть отрицательным (получено: {max_len})",
                )

        if min_len is not None and max_len is not None and min_len > max_len:
            raise argument_exception(
                "max_len",
                f"Минимальная длина ({min_len}) не может превышать максимальную ({max_len})!",
            )

        target_str = value.strip() if strip else value
        effective_len = len(target_str)

        if effective_len == 0:
            if allow_empty:
                return True
            raise argument_exception(field_name, "Пустой аргумент")

        if min_len is not None and effective_len < min_len:
            raise argument_exception(
                field_name,
                f"Длина строки меньше минимальной: ожидается не менее {min_len}",
            )

        if max_len is not None and effective_len > max_len:
            raise argument_exception(
                field_name,
                f"Некорректная длина аргумента: ожидается не более {max_len}",
            )

        return True

    @staticmethod
    def validate_number(
        value: Any,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        positive_only: bool = False,
        allow_nan: bool = False,
        allow_inf: bool = False,
        field_name: str = "",
    ) -> bool:
        """
        Валидация числового аргумента (int или float) с защитой от NaN и бесконечностей.

        Args:
            value (Any): Числовое значение
            min_value (int | float | None): Минимальное значение
            max_value (int | float | None): Максимальное значение
            positive_only (bool): Строго больше нуля (> 0)
            allow_nan (bool): Разрешать ли NaN (по умолчанию False)
            allow_inf (bool): Разрешать ли +/-Inf (по умолчанию False)
            field_name (str): Имя поля

        Returns:
            bool: True в случае успешной валидации
        """
        validator.validate_type(value, (int, float), field_name=field_name)

        if isinstance(value, float):
            if not allow_nan and math.isnan(value):
                raise argument_exception(
                    field_name,
                    "Числовое значение не может быть NaN (Not a Number)!",
                )
            if not allow_inf and math.isinf(value):
                raise argument_exception(
                    field_name,
                    "Числовое значение не может быть бесконечным (+/-Inf)!",
                )

        if min_value is not None:
            if isinstance(min_value, bool) or not isinstance(min_value, (int, float)):
                raise argument_exception(
                    "min_value",
                    f"Параметр 'min_value' должен быть числом, получено {type(min_value).__name__}",
                )
            if isinstance(min_value, float) and (math.isnan(min_value) or math.isinf(min_value)):
                raise argument_exception(
                    "min_value",
                    "Параметр 'min_value' не может быть NaN или бесконечностью!",
                )

        if max_value is not None:
            if isinstance(max_value, bool) or not isinstance(max_value, (int, float)):
                raise argument_exception(
                    "max_value",
                    f"Параметр 'max_value' должен быть числом, получено {type(max_value).__name__}",
                )
            if isinstance(max_value, float) and (math.isnan(max_value) or math.isinf(max_value)):
                raise argument_exception(
                    "max_value",
                    "Параметр 'max_value' не может быть NaN или бесконечностью!",
                )

        if min_value is not None and max_value is not None and min_value > max_value:
            raise argument_exception(
                "max_value",
                f"Минимальное значение ({min_value}) не может превышать максимальное ({max_value})!",
            )

        if positive_only:
            if max_value is not None and max_value <= 0:
                raise argument_exception(
                    "max_value",
                    f"Конфликт параметров: positive_only=True требует значение > 0, но max_value={max_value} <= 0!",
                )
            if value <= 0:
                raise argument_exception(
                    field_name,
                    "Число должно быть строго положительным (больше 0)",
                )

        if min_value is not None and value < min_value:
            raise argument_exception(
                field_name,
                f"Значение меньше допустимого минимума {min_value}",
            )

        if max_value is not None and value > max_value:
            raise argument_exception(
                field_name,
                f"Значение больше допустимого максимума {max_value}",
            )

        return True

    @staticmethod
    def validate_digits(
        value: Any,
        length: int | None = None,
        allowed_lengths: tuple[int, ...] | list[int] | set[int] | None = None,
        allow_int: bool = True,
        field_name: str = "",
    ) -> bool:
        """
        Валидация строки или целого числа, состоящего строго из ASCII цифр 0-9 (ИНН, БИК, счет).
        Защищает от инъекций Unicode-цифр ('¹²³', '١٢٣') и поддерживает int-значения.

        Args:
            value (Any): Строковое или целочисленное значение
            length (int | None): Точная требуемая длина
            allowed_lengths (tuple[int, ...] | list[int] | set[int] | None): Допустимые длины
            field_name (str): Имя поля

        Returns:
            bool: True в случае успешной валидации
        """
        if value is None:
            raise argument_exception(field_name, "Пустой аргумент")

        expected_types = (str, int) if allow_int else str
        expected_str = "str или int" if allow_int else "str"

        if isinstance(value, bool):
            raise argument_exception(
                field_name,
                f"Некорректный тип!\nОжидается {expected_str}. Текущий тип {type(value)}",
            )

        if not isinstance(value, expected_types):
            raise argument_exception(
                field_name,
                f"Некорректный тип!\nОжидается {expected_str}. Текущий тип {type(value)}",
            )

        if length is not None:
            if isinstance(length, bool) or not isinstance(length, int):
                raise argument_exception(
                    "length",
                    f"Параметр 'length' должен быть целым числом, получено {type(length).__name__}",
                )
            if length <= 0:
                raise argument_exception(
                    "length",
                    f"Параметр 'length' должен быть положительным числом (> 0), получено {length}",
                )

        if allowed_lengths is not None:
            if not isinstance(allowed_lengths, (tuple, list, set)):
                raise argument_exception(
                    "allowed_lengths",
                    f"Параметр 'allowed_lengths' должен быть коллекцией целых чисел, получен {type(allowed_lengths).__name__}",
                )
            for item in allowed_lengths:
                if isinstance(item, bool) or not isinstance(item, int) or item <= 0:
                    raise argument_exception(
                        "allowed_lengths",
                        f"Элементы 'allowed_lengths' должны быть положительными целыми числами, получено {repr(item)}",
                    )
            if length is not None and length not in allowed_lengths:
                raise argument_exception(
                    "length",
                    f"Параметр length ({length}) не входит в allowed_lengths ({allowed_lengths})!",
                )

        if isinstance(value, int):
            if value < 0:
                raise argument_exception(field_name, "Числовое значение не может быть отрицательным!")
            str_val = str(value)
        else:
            str_val = value.strip()
            if len(str_val) == 0:
                raise argument_exception(field_name, "Пустой аргумент")

        # Строгая проверка на ASCII цифры '0'-'9':
        # str.isdigit() пропускает юникодные надстрочные, подстрочные и региональные цифры ('¹²³', '١٢٣').
        if not (str_val.isascii() and str_val.isdigit()):
            raise argument_exception(field_name, "Значение должно состоять только из цифр!")

        if length is not None and len(str_val) != length:
            raise argument_exception(
                field_name,
                f"Длина должна содержать ровно {length} цифр!",
            )

        if allowed_lengths is not None and len(str_val) not in allowed_lengths:
            raise argument_exception(
                field_name,
                f"Длина должна соответствовать допустимой: {allowed_lengths}!",
            )

        return True


