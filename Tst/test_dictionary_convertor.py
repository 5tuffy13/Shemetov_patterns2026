import sys
import pytest
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Core.exception import argument_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.dictionary_convertor import dictionary_convertor


class test_dictionary_convertor:
    """
    Тестирование конвертера словарей
    """

    def test_success_dictionary_convertor_primitives(self):
        """
        <summary>
        Проверка преобразования словаря с примитивными значениями
        </summary>
        """
        # Подготовка
        factory = convert_factory()
        conv = dictionary_convertor(factory=factory)
        raw_dict = {"count": 10, "label": "тест", "active": True}

        # Действие
        res = conv.convert(raw_dict)

        # Проверка
        assert isinstance(res, dict)
        assert res == {"count": 10, "label": "тест", "active": True}

    def test_success_dictionary_convertor_none(self):
        """
        <summary>
        Проверка возврата пустого словаря при передаче None
        </summary>
        """
        # Подготовка
        conv = dictionary_convertor()

        # Действие
        res = conv.convert(None)

        # Проверка
        assert res == {}

    def test_fail_dictionary_convertor_invalid_type(self):
        """
        <summary>
        Проверка выброса исключения при передаче не-словаря
        </summary>
        """
        # Подготовка
        conv = dictionary_convertor()

        # Действие и Проверка
        with pytest.raises(argument_exception):
            conv.convert("не словарь")
