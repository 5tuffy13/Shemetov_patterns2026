import sys
import pytest
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Core.exception import argument_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.list_convertor import list_convertor
from Src.Models.range_model import range_model


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
        # Arrange
        factory = convert_factory()
        conv = list_convertor(factory=factory)
        raw_list = [1, 2, "три", 4.5]

        # Act
        res = conv.convert(raw_list)

        # Assert
        assert isinstance(res, list)
        assert res == [1, 2, "три", 4.5]

    def test_success_list_convertor_none_and_empty(self):
        """
        <summary>
        Проверка обработки None и пустых списков
        </summary>
        """
        # Arrange
        conv = list_convertor()

        # Act
        res_none = conv.convert(None)
        res_empty = conv.convert([])

        # Assert
        assert res_none == []
        assert res_empty == []

    def test_fail_list_convertor_non_collection_type(self):
        """
        <summary>
        Проверка выброса исключения при передаче одиночного не-коллекционного объекта
        </summary>
        """
        # Arrange
        conv = list_convertor()

        # Act & Assert
        with pytest.raises(argument_exception):
            conv.convert(12345)

    def test_success_list_convertor_deserialize_domain_models(self):
        """
        <summary>
        Проверка полиморфной десериализации списка сущностей через list_convertor
        </summary>
        """
        # Arrange
        factory = convert_factory()
        conv = factory.create(list)
        gram = range_model("грамм", 1)
        kg = range_model("килограмм", 1000, gram)

        serialized = conv.convert([gram, kg])
        assert isinstance(serialized, list)
        assert len(serialized) == 2
        assert "type" in serialized[0]

        # Act
        restored = conv.deserialize(serialized)

        # Assert
        assert isinstance(restored, list)
        assert len(restored) == 2
        assert isinstance(restored[0], range_model)
        assert isinstance(restored[1], range_model)
        assert restored[0].name == "грамм"
        assert restored[1].name == "килограмм"
        assert restored[1].base_range.id == restored[0].id
