"""
Модуль валидации данных
"""

from typing import Any
from Src.Core.exception import argument_exception, operation_exception


class validator:
    """
    Набор проверок корректности данных
    """

    @staticmethod
    def validate(
        value: Any,
        type_: type | tuple[type, ...],
        len_: int | None = None,
        field_name: str = "",
    ) -> bool:
        """
        Валидация аргумента по типу и длине (совместимость с эталонным проектом Patterns2026)

        Args:
            value (Any): Проверяемый аргумент
            type_ (type | tuple[type, ...]): Ожидаемый тип или кортеж типов
            len_ (int | None, optional): Максимальная длина. По умолчанию None.
            field_name (str, optional): Имя поля (для информативного исключения). По умолчанию "".

        Raises:
            argument_exception: Пустой аргумент
            argument_exception: Некорректный тип
            argument_exception: Некорректная длина аргумента

        Returns:
            bool: True в случае успешной валидации
        """
        if value is None:
            raise argument_exception(field_name, "Пустой аргумент")

        # Защита от Python-особенности: bool является подклассом int (isinstance(True, int) == True)
        if isinstance(value, bool):
            if type_ is not bool and (
                type_ is int or (isinstance(type_, tuple) and int in type_ and bool not in type_)
            ):
                raise argument_exception(
                    field_name,
                    f"Некорректный тип!\nОжидается {type_}. Текущий тип {type(value)}",
                )

        # Проверка типа
        if not isinstance(value, type_):
            raise argument_exception(
                field_name,
                f"Некорректный тип!\nОжидается {type_}. Текущий тип {type(value)}",
            )

        # Проверка непустого аргумента и длины для строк
        if isinstance(value, str):
            stripped = value.strip()
            if len(stripped) == 0:
                raise argument_exception(field_name, "Пустой аргумент")
            if len_ is not None and len(stripped) > len_:
                raise argument_exception(
                    field_name,
                    f"Некорректная длина аргумента: ожидается не более {len_}",
                )
        # Проверка для числовых значений (в эталонном проекте длина проверяется по строковому представлению)
        elif isinstance(value, (int, float)):
            str_repr = str(value).strip()
            if len(str_repr) == 0:
                raise argument_exception(field_name, "Пустой аргумент")
            if len_ is not None and len(str_repr) > len_:
                raise argument_exception(
                    field_name,
                    f"Некорректная длина аргумента: ожидается не более {len_}",
                )
        else:
            # Для произвольных объектов и коллекций
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
    def validate_type(
        value: Any,
        type_: type | tuple[type, ...],
        field_name: str = "",
    ) -> bool:
        """
        Проверка соответствия типа значения

        Args:
            value (Any): Проверяемый аргумент
            type_ (type | tuple[type, ...]): Ожидаемый тип
            field_name (str, optional): Имя поля

        Returns:
            bool: True в случае успешной валидации
        """
        if value is None:
            raise argument_exception(field_name, "Пустой аргумент")

        if isinstance(value, bool) and type_ is not bool and (
            type_ is int or (isinstance(type_, tuple) and int in type_ and bool not in type_)
        ):
            raise argument_exception(
                field_name,
                f"Некорректный тип!\nОжидается {type_}. Текущий тип {type(value)}",
            )

        if not isinstance(value, type_):
            raise argument_exception(
                field_name,
                f"Некорректный тип!\nОжидается {type_}. Текущий тип {type(value)}",
            )

        return True

    @staticmethod
    def validate_string(
        value: Any,
        min_len: int | None = None,
        max_len: int | None = None,
        allow_empty: bool = False,
        field_name: str = "",
    ) -> bool:
        """
        Валидация строкового аргумента с поддержкой минимальной и максимальной длины

        Args:
            value (Any): Строковое значение
            min_len (int | None): Минимальная длина
            max_len (int | None): Максимальная длина
            allow_empty (bool): Разрешать ли пустую строку
            field_name (str): Имя поля

        Returns:
            bool: True в случае успешной валидации
        """
        validator.validate_type(value, str, field_name=field_name)
        stripped = value.strip()

        if not allow_empty and len(stripped) == 0:
            raise argument_exception(field_name, "Пустой аргумент")

        if min_len is not None and len(stripped) < min_len:
            raise argument_exception(
                field_name,
                f"Длина строки меньше минимальной: ожидается не менее {min_len}",
            )

        if max_len is not None and len(stripped) > max_len:
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
        field_name: str = "",
    ) -> bool:
        """
        Валидация числового аргумента (int или float) с проверкой диапазонов

        Args:
            value (Any): Числовое значение
            min_value (int | float | None): Минимальное значение
            max_value (int | float | None): Максимальное значение
            positive_only (bool): Строго больше нуля
            field_name (str): Имя поля

        Returns:
            bool: True в случае успешной валидации
        """
        validator.validate_type(value, (int, float), field_name=field_name)

        if positive_only and value <= 0:
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
        allowed_lengths: tuple[int, ...] | list[int] | None = None,
        field_name: str = "",
    ) -> bool:
        """
        Валидация строки, состоящей строго из цифр (ИНН, БИК, расчетный счет)

        Args:
            value (Any): Строковое значение из цифр
            length (int | None): Точная длина
            allowed_lengths (tuple[int, ...] | list[int] | None): Набор допустимых длин
            field_name (str): Имя поля

        Returns:
            bool: True в случае успешной валидации
        """
        validator.validate_type(value, str, field_name=field_name)
        stripped = value.strip()

        if not stripped.isdigit():
            raise argument_exception(field_name, "Значение должно состоять только из цифр!")

        if length is not None and len(stripped) != length:
            raise argument_exception(
                field_name,
                f"Длина должна содержать ровно {length} цифр!",
            )

        if allowed_lengths is not None and len(stripped) not in allowed_lengths:
            raise argument_exception(
                field_name,
                f"Длина должна соответствовать допустимой: {allowed_lengths}!",
            )

        return True
