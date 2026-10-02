"""
Модульные тесты для менеджера хранения данных (storage_manager)
Кандидат 1: Direct Registry Storage & Static Seed Factory
Автор: Alexander
"""

import sys
import pytest
from pathlib import Path

# Добавление путей для запуска тестов
repo_root = Path("/opt/data/vault/study/assignments/patterns/Shemetov_patterns2026")
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

candidate_dir = Path("/tmp/arena-caching/candidate-1")
if str(candidate_dir) not in sys.path:
    sys.path.insert(0, str(candidate_dir))

from Src.Logics.storage_manager import storage_manager
from Src.Core.validator import argument_exception, operation_exception
from Src.Models.storage_model import storage_model
from Src.Models.range_model import range_model
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Logics.settings_manager import settings_manager


@pytest.fixture(autouse=True)
def clean_storage():
    """
    Фикстура для очистки состояния хранилища перед каждым тестом
    """
    manager = storage_manager()
    manager.clear()
    yield
    manager.clear()


def test_success_storage_manager_singleton_identity():
    """
    <summary>
    Проверка работы шаблона Singleton для storage_manager.
    Ожидается: повторные вызовы конструктора возвращают идентичный экземпляр в памяти (is).
    </summary>
    """
    instance1 = storage_manager()
    instance2 = storage_manager()
    assert instance1 is instance2


def test_success_storage_manager_singleton_shared_state():
    """
    <summary>
    Проверка разделения состояния между ссылками на Singleton storage_manager.
    Ожидается: добавление сущности через одну ссылку мгновенно доступно через другую ссылку.
    </summary>
    """
    manager1 = storage_manager()
    manager2 = storage_manager()

    unit = range_model("миллилитр", 1)
    manager1.add_range(unit)

    assert len(manager2.ranges) == 1
    assert manager2.get_range(unit.id) == unit
    assert manager2.get_range("миллилитр") == unit


def test_success_storage_manager_convert_generates_default_entities():
    """
    <summary>
    Проверка генерации первичных данных при вызове convert() в режиме первого старта.
    Ожидается: метод convert() возвращает True, наполняет хранилище и переключает флаги.
    </summary>
    """
    manager = storage_manager()
    result = manager.convert(is_first=True)

    assert result is True
    assert manager.is_loaded is True
    assert manager.is_first_start is False
    assert len(manager.storages) == 3
    assert len(manager.ranges) == 5
    assert len(manager.groups) == 4
    assert len(manager.nomenclatures) == 7


def test_success_storage_manager_convert_when_is_first_false():
    """
    <summary>
    Проверка поведения метода convert() при отключенном флаге первого запуска (is_first=False).
    Ожидается: если хранилище пусто, первичные данные не создаются, возвращается False.
    </summary>
    """
    manager = storage_manager()
    result = manager.convert(is_first=False)

    assert result is False
    assert len(manager.storages) == 0
    assert len(manager.ranges) == 0
    assert len(manager.groups) == 0
    assert len(manager.nomenclatures) == 0


def test_success_storage_manager_first_start_populates_all_categories():
    """
    <summary>
    Проверка наполнения всех 4 категорий данных методом first_start().
    Ожидается: в хранилище присутствуют склады, единицы измерения, группы и номенклатура.
    </summary>
    """
    manager = storage_manager()
    manager.first_start()

    assert len(manager.storages) > 0
    assert len(manager.ranges) > 0
    assert len(manager.groups) > 0
    assert len(manager.nomenclatures) > 0


def test_success_storage_manager_load_from_settings():
    """
    <summary>
    Проверка интеграции storage_manager с settings_manager.
    Ожидается: метод load_from_settings успешно инициализирует состояние хранилища.
    </summary>
    """
    manager = storage_manager()
    settings_mgr = settings_manager()

    manager.load_from_settings(settings_mgr)
    assert manager.is_loaded is True
    assert len(manager.storages) > 0


def test_fail_storage_manager_invalid_is_first_type():
    """
    <summary>
    Проверка выброса исключения при передаче невалидного типа для флага is_first.
    Ожидается: argument_exception при передаче int, str или float вместо bool.
    </summary>
    """
    manager = storage_manager()

    with pytest.raises(argument_exception):
        manager.convert(is_first="true")

    with pytest.raises(argument_exception):
        manager.convert(is_first=123)

    with pytest.raises(argument_exception):
        manager.is_first_start = "invalid_flag"


def test_fail_storage_manager_load_non_existent_file():
    """
    <summary>
    Проверка выброса исключения при попытке загрузки несуществующего файла.
    Ожидается: operation_exception при передаче пути к отсутствующему файлу.
    </summary>
    """
    manager = storage_manager()
    with pytest.raises(operation_exception):
        manager.load("missing_file_for_test_12345.json")


def test_fail_storage_manager_load_invalid_file_type():
    """
    <summary>
    Проверка выброса исключения при передаче нестрокового типа пути в метод load().
    Ожидается: argument_exception при передаче int, list или другого типа.
    </summary>
    """
    manager = storage_manager()
    with pytest.raises(argument_exception):
        manager.load(12345)


def test_fail_storage_manager_duplicate_id_raises_operation_exception():
    """
    <summary>
    Проверка обеспечения строгого запрета дублирования по идентификатору (id).
    Ожидается: operation_exception при повторном добавлении сущности с уже существующим id.
    </summary>
    """
    manager = storage_manager()
    unit1 = range_model("штука", 1)
    unit2 = range_model("шт", 1)
    unit2.id = unit1.id

    manager.add_range(unit1)
    with pytest.raises(operation_exception):
        manager.add_range(unit2)


def test_fail_storage_manager_duplicate_name_raises_operation_exception():
    """
    <summary>
    Проверка обеспечения строгого запрета дублирования по наименованию (name).
    Ожидается: operation_exception при повторном добавлении сущности с уже существующим именем.
    </summary>
    """
    manager = storage_manager()
    storage1 = storage_model("Главный склад", "Адрес 1")
    storage2 = storage_model("Главный склад", "Адрес 2")

    manager.add_storage(storage1)
    with pytest.raises(operation_exception):
        manager.add_storage(storage2)


def test_fail_storage_manager_duplicate_storage_raises_operation_exception():
    """
    <summary>
    Проверка уникальности складов в хранилище.
    Ожидается: operation_exception при попытке зарегистрировать склад-дубликат.
    </summary>
    """
    manager = storage_manager()
    s1 = storage_model("Склад №1", "ул. Первая, 1")
    s2 = storage_model("Склад №1", "ул. Вторая, 2")

    manager.add_storage(s1)
    with pytest.raises(operation_exception):
        manager.add_storage(s2)


def test_fail_storage_manager_duplicate_range_raises_operation_exception():
    """
    <summary>
    Проверка уникальности единиц измерения в хранилище.
    Ожидается: operation_exception при попытке зарегистрировать единицу-дубликат.
    </summary>
    """
    manager = storage_manager()
    r1 = range_model("литр", 1)
    r2 = range_model("литр", 1)

    manager.add_range(r1)
    with pytest.raises(operation_exception):
        manager.add_range(r2)


def test_fail_storage_manager_duplicate_group_raises_operation_exception():
    """
    <summary>
    Проверка уникальности групп номенклатуры в хранилище.
    Ожидается: operation_exception при попытке зарегистрировать группу-дубликат.
    </summary>
    """
    manager = storage_manager()
    g1 = nomenclature_group_model("Сырье")
    g2 = nomenclature_group_model("Сырье")

    manager.add_group(g1)
    with pytest.raises(operation_exception):
        manager.add_group(g2)


def test_fail_storage_manager_duplicate_nomenclature_raises_operation_exception():
    """
    <summary>
    Проверка уникальности позиций номенклатуры в хранилище.
    Ожидается: operation_exception при попытке зарегистрировать номенклатуру-дубликат.
    </summary>
    """
    manager = storage_manager()
    group = nomenclature_group_model("Ингредиенты")
    unit = range_model("кг", 1)
    nom1 = nomenclature_model("Сахар", "Сахар белый", group, unit)
    nom2 = nomenclature_model("Сахар", "Сахар тростниковый", group, unit)

    manager.add_group(group)
    manager.add_range(unit)
    manager.add_nomenclature(nom1)
    with pytest.raises(operation_exception):
        manager.add_nomenclature(nom2)


def test_fail_storage_manager_invalid_model_type_registration():
    """
    <summary>
    Проверка типобезопасности при регистрации сущностей в несоответствующие реестры.
    Ожидается: argument_exception при передаче неподходящего типа модели.
    </summary>
    """
    manager = storage_manager()
    unit = range_model("грамм", 1)

    with pytest.raises(argument_exception):
        manager.add_storage(unit)


def test_success_storage_manager_get_by_id_and_name():
    """
    <summary>
    Проверка быстрого доступа к данным за O(1) по id и наименованию.
    Ожидается: успешный возврат целевой сущности по ее ключам.
    </summary>
    """
    manager = storage_manager()
    group = nomenclature_group_model("Бакалея")
    unit = range_model("грамм", 1)
    nom = nomenclature_model("Мука", "Мука высший сорт", group, unit)

    manager.add_group(group)
    manager.add_range(unit)
    manager.add_nomenclature(nom)

    assert manager.get_group(group.id) == group
    assert manager.get_group("Бакалея") == group
    assert manager.get_range(unit.id) == unit
    assert manager.get_range("грамм") == unit
    assert manager.get_nomenclature(nom.id) == nom
    assert manager.get_nomenclature("Мука") == nom

    # Несуществующие значения возвращают None
    assert manager.get_group("Неизвестная группа") is None
    assert manager.get_storage("Неизвестный склад") is None


def test_success_storage_manager_dict_accessors():
    """
    <summary>
    Проверка свойств прямого доступа к словарям сущностей по id (O(1)).
    Ожидается: свойства возвращают словари с ключами id и значениями-объектами.
    </summary>
    """
    manager = storage_manager()
    manager.first_start()

    storages_dict = manager.storages_dict
    ranges_dict = manager.ranges_dict
    groups_dict = manager.groups_dict
    nomenclatures_dict = manager.nomenclatures_dict

    assert isinstance(storages_dict, dict)
    assert isinstance(ranges_dict, dict)
    assert isinstance(groups_dict, dict)
    assert isinstance(nomenclatures_dict, dict)

    assert len(storages_dict) == 3
    assert len(ranges_dict) == 5
    assert len(groups_dict) == 4
    assert len(nomenclatures_dict) == 7


def test_success_storage_manager_recipe_ingredients_present():
    """
    <summary>
    Проверка наличия всех ключевых ингредиентов рецепта «Вафли хрустящие» в первичных данных.
    Ожидается: в хранилище присутствуют мука, сахар, масло, яйцо, молоко, ванилин и само блюдо.
    </summary>
    """
    manager = storage_manager()
    manager.first_start()

    expected_items = [
        "Мука пшеничная",
        "Сахар",
        "Сливочное масло",
        "Яйцо куриное",
        "Молоко",
        "Ванилин",
        "Вафли хрустящие",
    ]

    for item_name in expected_items:
        item = manager.get_nomenclature(item_name)
        assert item is not None
        assert item.name == item_name
        assert item.group is not None
        assert item.range is not None
