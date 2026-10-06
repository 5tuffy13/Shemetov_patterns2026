import sys
import pytest
from pathlib import Path

# Определение корня проекта
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Core.exception import argument_exception, operation_exception
from Src.Models.range_model import range_model
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.receipt_row_model import receipt_row_model
from Src.Models.receipt_model import receipt_model
from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model


@pytest.fixture(autouse=True)
def clean_storage():
    """
    Фикстура изоляции тестов: очистка хранилища до и после теста
    """
    manager = storage_manager()
    manager.clear()
    yield
    manager.clear()


# -----------------------------------------------------------------------------
# Тесты строки рецепта (receipt_row_model)
# -----------------------------------------------------------------------------

def test_success_receipt_row_model_create():
    """
    <summary>
    Проверка создания строки технологической карты со всеми свойствами.
    Ожидается: свойства номенклатуры, единицы измерения и весов инициализированы.
    </summary>
    """
    # Подготовка
    unit = range_model("грамм", 1)
    group = nomenclature_group_model("Бакалея")
    item = nomenclature_model("Сахар", "Сахар белый", group, unit)

    # Действие
    row = receipt_row_model(item, gross=100.0, net=95.0)

    # Проверка
    assert row.nomenclature == item
    assert row.name == "Сахар"
    assert row.range == unit
    assert row.gross == 100.0
    assert row.net == 95.0
    assert row.gross_weight == 100.0
    assert row.net_weight == 95.0


def test_success_receipt_row_model_set_weights():
    """
    <summary>
    Проверка синхронной установки весов брутто и нетто методом set_weights.
    Ожидается: веса брутто и нетто обновлены корректно.
    </summary>
    """
    # Подготовка
    row = receipt_row_model()

    # Действие
    row.set_weights(50.0, 45.0)

    # Проверка
    assert row.gross == 50.0
    assert row.net == 45.0


def test_fail_receipt_row_model_net_exceeds_gross():
    """
    <summary>
    Проверка инварианта: масса нетто не может превышать массу брутто.
    Ожидается: выброс argument_exception.
    </summary>
    """
    # Подготовка
    row = receipt_row_model()
    row.set_weights(100.0, 100.0)

    # Действие и Проверка
    with pytest.raises(argument_exception):
        row.net = 105.0


def test_fail_receipt_row_model_gross_less_than_net():
    """
    <summary>
    Проверка инварианта: масса брутто не может быть меньше массы нетто.
    Ожидается: выброс argument_exception.
    </summary>
    """
    # Подготовка
    row = receipt_row_model()
    row.set_weights(100.0, 90.0)

    # Действие и Проверка
    with pytest.raises(argument_exception):
        row.gross = 85.0


def test_fail_receipt_row_model_negative_or_zero_weight():
    """
    <summary>
    Проверка валидации неположительных значений массы.
    Ожидается: выброс argument_exception при значении <= 0.
    </summary>
    """
    # Подготовка
    row = receipt_row_model()

    # Действие и Проверка
    with pytest.raises(argument_exception):
        row.gross = -10.0

    with pytest.raises(argument_exception):
        row.net = 0.0


def test_fail_receipt_row_model_invalid_types():
    """
    <summary>
    Проверка валидации типов номенклатуры и единицы измерения в строке рецепта.
    Ожидается: выброс argument_exception при передаче некорректных типов.
    </summary>
    """
    # Подготовка
    row = receipt_row_model()

    # Действие и Проверка
    with pytest.raises(argument_exception):
        row.nomenclature = "Некорректная номенклатура"

    with pytest.raises(argument_exception):
        row.range = 100


# -----------------------------------------------------------------------------
# Тесты технологической карты (receipt_model)
# -----------------------------------------------------------------------------

def test_success_receipt_model_create_and_totals():
    """
    <summary>
    Проверка создания технологической карты и подсчета суммарных весов брутто и нетто.
    Ожидается: суммарные веса брутто и нетто равны сумме по строкам.
    </summary>
    """
    # Подготовка
    unit = range_model("грамм", 1)
    group = nomenclature_group_model("Бакалея")
    flour = nomenclature_model("Мука", "Мука пшеничная", group, unit)
    sugar = nomenclature_model("Сахар", "Сахар песок", group, unit)

    row1 = receipt_row_model(flour, gross=100.0, net=100.0)
    row2 = receipt_row_model(sugar, gross=80.0, net=80.0)

    # Действие
    receipt = receipt_model("Песочное тесто", portions=4, cooking_time=30)
    receipt.add_row(row1)
    receipt.add_row(row2)

    # Проверка
    assert receipt.name == "Песочное тесто"
    assert receipt.portions == 4
    assert receipt.cooking_time == 30
    assert len(receipt.rows) == 2
    assert receipt.gross == 180.0
    assert receipt.net == 180.0
    assert receipt.gross_weight == 180.0
    assert receipt.net_weight == 180.0


def test_fail_receipt_model_duplicate_nomenclature():
    """
    <summary>
    Проверка инварианта уникальности номенклатуры в рамках одного рецепта.
    Ожидается: выброс argument_exception при повторном добавлении той же номенклатуры.
    </summary>
    """
    # Подготовка
    unit = range_model("грамм", 1)
    group = nomenclature_group_model("Бакалея")
    flour = nomenclature_model("Мука", "Мука пшеничная", group, unit)

    row1 = receipt_row_model(flour, gross=100.0, net=100.0)
    row2 = receipt_row_model(flour, gross=50.0, net=50.0)
    receipt = receipt_model("Рецепт")
    receipt.add_row(row1)

    # Действие и Проверка
    with pytest.raises(argument_exception):
        receipt.add_row(row2)


def test_fail_receipt_model_invalid_portions_and_time():
    """
    <summary>
    Проверка валидации параметров количества порций и времени приготовления.
    Ожидается: выброс argument_exception при неположительных порциях или отрицательном времени.
    </summary>
    """
    # Подготовка
    receipt = receipt_model("Рецепт")

    # Действие и Проверка
    with pytest.raises(argument_exception):
        receipt.portions = 0

    with pytest.raises(argument_exception):
        receipt.cooking_time = -5


# -----------------------------------------------------------------------------
# Тест рецептуры вафель (BaseReceipt.md)
# -----------------------------------------------------------------------------

def test_success_receipt_model_waffles_spec():
    """
    <summary>
    Проверка расчета массы брутто и нетто для рецептуры «Вафли хрустящие в вафельнице»
    на 10 порций согласно BaseReceipt.md.
    Ожидается: Брутто = 305.0 г, Нетто = 298.0 г.
    </summary>
    """
    # Подготовка
    unit_gram = range_model("грамм", 1)
    unit_piece = range_model("штука", 1)
    group = nomenclature_group_model("Ингредиенты")

    flour = nomenclature_model("Пшеничная мука", "Мука пшеничная", group, unit_gram)
    sugar = nomenclature_model("Сахар", "Сахар песок", group, unit_gram)
    butter = nomenclature_model("Сливочное масло", "Масло сливочное", group, unit_gram)
    egg = nomenclature_model("Яйцо куриное", "Яйцо столовое", group, unit_piece)
    vanilla = nomenclature_model("Ванилин", "Ванилин кристаллический", group, unit_gram)

    # Действие
    receipt = receipt_model("Вафли хрустящие в вафельнице", portions=10, cooking_time=20)
    receipt.add_row(receipt_row_model(flour, gross=100.0, net=100.0, range=unit_gram))
    receipt.add_row(receipt_row_model(sugar, gross=80.0, net=80.0, range=unit_gram))
    receipt.add_row(receipt_row_model(butter, gross=70.0, net=70.0, range=unit_gram))
    receipt.add_row(receipt_row_model(egg, gross=50.0, net=43.0, range=unit_piece))
    receipt.add_row(receipt_row_model(vanilla, gross=5.0, net=5.0, range=unit_gram))

    # Проверка
    assert receipt.gross == 305.0
    assert receipt.net == 298.0
    assert receipt.portions == 10
    assert receipt.cooking_time == 20


# -----------------------------------------------------------------------------
# Тесты интеграции с хранилищем (storage_manager)
# -----------------------------------------------------------------------------

def test_success_storage_manager_first_start_seed():
    """
    <summary>
    Проверка добавления технологической карты вафель в хранилище при первом старте.
    Ожидается: рецепт присутствует в storage_manager с 5 ингредиентами и весами 305/298.
    </summary>
    """
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)

    # Действие
    result = manager.build()

    # Проверка
    assert result is True
    assert storage_manager.receipt_key() in storage_manager.keys()
    assert len(manager.receipts) == 1

    waffle_recipe = manager.get_receipt("Вафли хрустящие в вафельнице")
    assert waffle_recipe is not None
    assert waffle_recipe.gross == 305.0
    assert waffle_recipe.net == 298.0
    assert waffle_recipe.portions == 10
    assert len(waffle_recipe.rows) == 5


def test_fail_storage_manager_duplicate_receipt():
    """
    <summary>
    Проверка контроля уникальности наименования рецепта при добавлении в хранилище.
    Ожидается: выброс operation_exception при дублировании имени.
    </summary>
    """
    # Подготовка
    manager = storage_manager()
    r1 = receipt_model("Рецепт вафель")
    r2 = receipt_model("Рецепт вафель")
    manager.add_receipt(r1)

    # Действие и Проверка
    with pytest.raises(operation_exception):
        manager.add_receipt(r2)
