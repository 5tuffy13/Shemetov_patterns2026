import pytest
from Src.Core.abstract_reference import abstract_reference
from Src.Core.exception import argument_exception


class test_entity(abstract_reference):
    """
    Тестовый класс для проверки абстрактной сущности
    """
    pass


def test_success_abstract_model_id_not_null():
    """
    <summary>
    Проверка генерации непустого id при создании объекта.
    Ожидается: сгенерированный строковый id не пустой.
    </summary>
    """
    entity = test_entity()
    assert entity.id != ""


def test_fail_abstract_model_name_empty():
    """
    <summary>
    Проверка выброса исключения при попытке установить пустое имя.
    Ожидается: argument_exception при присвоении пустой строки.
    </summary>
    """
    obj = test_entity()
    with pytest.raises(argument_exception):
        obj.name = ""


def test_success_abstract_model_equals_by_id():
    """
    <summary>
    Проверка равенства двух объектов при совпадении их id.
    Ожидается: объекты равны при одинаковых id.
    </summary>
    """
    ob1 = test_entity()
    ob2 = test_entity()
    ob1.id = "000"
    ob2.id = "000"
    assert ob1 == ob2


def test_success_abstract_model_id_is_unique():
    """
    <summary>
    Проверка уникальности автоматически сгенерированных id.
    Ожидается: два разных объекта имеют различные id.
    </summary>
    """
    ob1 = test_entity()
    ob2 = test_entity()
    assert ob1.id != ob2.id


def test_fail_abstract_model_get_name_before_assignment():
    """
    <summary>
    Проверка обращения к свойству name до его инициализации.
    Ожидается: выброс argument_exception с сообщением о незаданном имени.
    </summary>
    """
    obj = test_entity()
    with pytest.raises(argument_exception):
        _ = obj.name


def test_fail_abstract_model_name_invalid_type():
    """
    <summary>
    Проверка выброса исключения при передаче нестрокового типа в name.
    Ожидается: argument_exception при присвоении нестроки.
    </summary>
    """
    obj = test_entity()
    with pytest.raises(argument_exception):
        obj.name = 12345


def test_fail_abstract_model_name_whitespace_only():
    """
    <summary>
    Проверка выброса исключения при присвоении имени из одних пробелов.
    Ожидается: argument_exception при значении из пробелов.
    </summary>
    """
    obj = test_entity()
    with pytest.raises(argument_exception):
        obj.name = "   "


def test_success_abstract_model_name_strip():
    """
    <summary>
    Проверка автоматического удаления пробельных символов по краям имени.
    Ожидается: пробелы по краям удалены при присвоении.
    </summary>
    """
    obj = test_entity()
    obj.name = "  Тест  "
    assert obj.name == "Тест"


def test_success_abstract_model_set_valid_id():
    """
    <summary>
    Проверка возможности установки валидного id.
    Ожидается: свойство id обновляется переданным значением.
    </summary>
    """
    obj = test_entity()
    obj.id = "custom-id-123"
    assert obj.id == "custom-id-123"


def test_fail_abstract_model_set_empty_id():
    """
    <summary>
    Проверка выброса исключения при попытке установить пустой id.
    Ожидается: argument_exception при передаче пустой строки или строки из пробелов в id.
    </summary>
    """
    obj = test_entity()
    with pytest.raises(argument_exception):
        obj.id = "   "


def test_success_abstract_model_not_equals_different_ids():
    """
    <summary>
    Проверка неравенства объектов с разными id.
    Ожидается: оператор == возвращает False при разных id.
    </summary>
    """
    ob1 = test_entity()
    ob2 = test_entity()
    ob1.id = "id_1"
    ob2.id = "id_2"
    assert ob1 != ob2
