import sys
import pytest
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Core.exception import argument_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.list_convertor import list_convertor


class test_list_convertor:
    """
    Тестирование конвертера коллекций и списков
    """

    def test_success_list_convertor_primitives(self):
        """
        <summary>
        Проверка преобразования списка примитивных элементов с делегированием в фабрику
        </summary>
        """
        # Подготовка
        factory = convert_factory()
        conv = list_convertor(factory=factory)
        raw_list = [1, 2, "три", 4.5]

        # Действие
        res = conv.convert(raw_list)

        # Проверка
        assert isinstance(res, list)
        assert res == [1, 2, "три", 4.5]

    def test_success_list_convertor_none_and_empty(self):
        """
        <summary>
        Проверка обработки None и пустых списков
        </summary>
        """
        # Подготовка
        conv = list_convertor()

        # Действие
        res_none = conv.convert(None)
        res_empty = conv.convert([])

        # Проверка
        assert res_none == []
        assert res_empty == []

    def test_fail_list_convertor_non_collection_type(self):
        """
        <summary>
        Проверка выброса исключения при передаче одиночного не-коллекционного объекта
        </summary>
        """
        # Подготовка
        conv = list_convertor()

        # Действие и Проверка
        with pytest.raises(argument_exception):
            conv.convert(12345)
