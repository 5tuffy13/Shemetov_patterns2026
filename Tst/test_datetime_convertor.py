import sys
import pytest
from datetime import date, datetime, time
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Core.exception import argument_exception
from Src.Logics.datetime_convertor import datetime_convertor


class test_datetime_convertor:
    """
    Тестирование конвертера объектов даты и времени
    """

    def test_success_datetime_convertor_iso_format(self):
        """
        <summary>
        Проверка преобразования объектов datetime, date и time в формат ISO 8601
        </summary>
        """
        # Подготовка
        conv = datetime_convertor()
        dt = datetime(2026, 10, 22, 14, 15, 30)
        d = date(2026, 10, 22)
        t = time(14, 15, 30)

        # Действие
        res_dt = conv.convert(dt)
        res_d = conv.convert(d)
        res_t = conv.convert(t)

        # Проверка
        assert res_dt == "2026-10-22T14:15:30"
        assert res_d == "2026-10-22"
        assert res_t == "14:15:30"

    def test_success_datetime_convertor_none(self):
        """
        <summary>
        Проверка возврата None при передаче пустого значения
        </summary>
        """
        # Подготовка
        conv = datetime_convertor()

        # Действие
        res = conv.convert(None)

        # Проверка
        assert res is None

    def test_fail_datetime_convertor_unsupported_type(self):
        """
        <summary>
        Проверка выброса исключения при передаче не-даты в конвертер
        </summary>
        """
        # Подготовка
        conv = datetime_convertor()

        # Действие и Проверка
        with pytest.raises(argument_exception):
            conv.convert("2026-10-22")
