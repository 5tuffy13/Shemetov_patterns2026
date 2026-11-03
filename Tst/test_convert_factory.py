import sys
import pytest
from datetime import datetime
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.exception import argument_exception
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.convert_factory import convert_factory
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.dictionary_convertor import dictionary_convertor
from Src.Logics.domain_convertor import domain_convertor
from Src.Logics.list_convertor import list_convertor
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.receipt_model import receipt_model


class test_convert_factory:
    """
    Тестирование фабрики конвертеров данных
    """

    @pytest.fixture(autouse=True)
    def setup_data(self):
        # Подготовка
        self.factory = convert_factory()

    def test_success_convert_factory_implements_interface(self):
        """
        <summary>
        Проверка реализации абстрактного интерфейса abstract_convert_factory
        </summary>
        """
        # Действие и Проверка
        assert isinstance(self.factory, abstract_convert_factory)

    def test_success_convert_factory_create_by_type(self):
        """
        <summary>
        Проверка фабричного метода create для подбора конвертеров по целевому типу данных
        </summary>
        """
        # Действие
        conv_int = self.factory.create(int)
        conv_dt = self.factory.create(datetime)
        conv_list = self.factory.create(list)
        conv_dict = self.factory.create(dict)
        conv_receipt = self.factory.create(receipt_model)
        conv_nom = self.factory.create(nomenclature_model)

        # Проверка
        assert isinstance(conv_int, basic_convertor)
        assert isinstance(conv_dt, datetime_convertor)
        assert isinstance(conv_list, list_convertor)
        assert isinstance(conv_dict, dictionary_convertor)
        assert isinstance(conv_receipt, domain_convertor)
        assert isinstance(conv_nom, domain_convertor)

    def test_success_convert_factory_create_by_instance(self):
        """
        <summary>
        Проверка создания конвертера при передаче экземпляра объекта
        </summary>
        """
        # Действие
        conv_num = self.factory.create(42)
        conv_str = self.factory.create("строка")

        # Проверка
        assert isinstance(conv_num, basic_convertor)
        assert isinstance(conv_str, basic_convertor)
