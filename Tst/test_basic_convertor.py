import sys
import pytest
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Core.exception import argument_exception
from Src.Logics.basic_convertor import basic_convertor


class test_basic_convertor:
    """
    Тестирование базового конвертера примитивных типов
    """

    def test_success_basic_convertor_numeric_and_boolean(self):
        """
        <summary>
        Проверка преобразования целых чисел, чисел с плавающей точкой и булевых значений
        </summary>
        """
        # Подготовка
        conv = basic_convertor()

        # Действие
        val_int = conv.convert(42)
        val_float = conv.convert(3.14)
        val_bool = conv.convert(True)

        # Проверка
        assert val_int == 42
        assert val_float == 3.14
        assert val_bool is True

    def test_success_basic_convertor_string_and_none(self):
        """
        <summary>
        Проверка преобразования строк и обработки значения None
        </summary>
        """
        # Подготовка
        conv = basic_convertor()

        # Действие
        val_str = conv.convert("Номенклатура")
        val_none = conv.convert(None)

        # Проверка
        assert val_str == "Номенклатура"
        assert val_none is None

    def test_fail_basic_convertor_unsupported_type(self):
        """
        <summary>
        Проверка выброса исключения при передаче неподдерживаемых сложных объектов
        </summary>
        """
        # Подготовка
        conv = basic_convertor()

        # Действие и Проверка
        with pytest.raises(argument_exception):
            conv.convert([1, 2, 3])
