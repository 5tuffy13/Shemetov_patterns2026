import sys
import pytest
from pathlib import Path

# Определение корня проекта
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Core.exception import argument_exception, operation_exception
from Src.Logics.storage_manager import storage_manager
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_row_model import receipt_row_model


class TestReceipt:
    """
    Набор тестов для технологической карты и ее строк
    """

    @pytest.fixture(autouse=True)
    def setup_data(self):
        """
        Инициализация фикстур тестовых данных
        """
        # Подготовка
        self.group = nomenclature_group_model("Сырье")
        self.unit_g = range_model("грамм", 1)
        self.unit_pcs = range_model("штука", 1)

        self.flour = nomenclature_model(
            name="Мука", full_name="Мука пшеничная", group=self.group, range=self.unit_g
        )
        self.water = nomenclature_model(
            name="Вода", full_name="Вода питьевая", group=self.group, range=self.unit_g
        )
        self.cheese = nomenclature_model(
            name="Сыр", full_name="Сыр Моцарелла", group=self.group, range=self.unit_g
        )

    # -------------------------------------------------------------------------
    # Тесты модели строки рецепта (receipt_row_model)
    # -------------------------------------------------------------------------

    def test_success_receipt_row_initialization_with_setters(self):
        """
        <summary>
        Проверка корректной инициализации строки рецепта и работы сеттеров
        </summary>
        """
        # Подготовка
        row = receipt_row_model()

        # Действие
        row.nomenclature = self.flour
        row.gross = 200.0
        row.net = 190.0

        # Проверка
        assert row.nomenclature == self.flour
        assert row.name == "Мука"
        assert row.range == self.unit_g
        assert row.gross == 200.0
        assert row.gross_weight == 200.0
        assert row.net == 190.0
        assert row.net_weight == 190.0

    def test_success_receipt_row_set_weights(self):
        """
        <summary>
        Проверка одновременной установки весов через set_weights
        </summary>
        """
        # Подготовка
        row = receipt_row_model(self.flour)

        # Действие
        row.set_weights(150.0, 140.0)

        # Проверка
        assert row.gross == 150.0
        assert row.net == 140.0

    def test_fail_receipt_row_gross_less_than_net(self):
        """
        <summary>
        Проверка выброса исключения при попытке установить gross меньше net
        </summary>
        """
        # Подготовка
        row = receipt_row_model(self.flour, gross=100.0, net=90.0)

        # Действие и проверка
        with pytest.raises(argument_exception) as exc_info:
            row.gross = 80.0

        assert "gross" in str(exc_info.value)
        assert "меньше" in str(exc_info.value)

    def test_fail_receipt_row_net_greater_than_gross(self):
        """
        <summary>
        Проверка выброса исключения при попытке установить net больше gross
        </summary>
        """
        # Подготовка
        row = receipt_row_model(self.flour, gross=100.0, net=90.0)

        # Действие и проверка
        with pytest.raises(argument_exception) as exc_info:
            row.net = 110.0

        assert "net" in str(exc_info.value)
        assert "превышать" in str(exc_info.value)

    def test_fail_receipt_row_invalid_types(self):
        """
        <summary>
        Проверка валидации некорректных типов аргументов в сеттерах строки рецепта
        </summary>
        """
        # Подготовка
        row = receipt_row_model()

        # Действие и проверка
        with pytest.raises(argument_exception):
            row.nomenclature = "не номенклатура"

        with pytest.raises(argument_exception):
            row.range = 12345

        with pytest.raises(argument_exception):
            row.gross = -50.0

        with pytest.raises(argument_exception):
            row.net = 0

    # -------------------------------------------------------------------------
    # Тесты модели технологической карты (receipt_model)
    # -------------------------------------------------------------------------

    def test_success_receipt_creation_and_row_addition(self):
        """
        <summary>
        Проверка успешного создания технологической карты и добавления строк
        </summary>
        """
        # Подготовка
        receipt = receipt_model("Тесто для пиццы", portions=1, cooking_time=60)
        row1 = receipt_row_model(self.flour, gross=180.0, net=180.0)
        row2 = receipt_row_model(self.water, gross=110.0, net=110.0)

        # Действие
        receipt.add_row(row1)
        receipt.add_row(row2)

        # Проверка
        assert receipt.name == "Тесто для пиццы"
        assert receipt.portions == 1
        assert receipt.cooking_time == 60
        assert len(receipt.rows) == 2
        assert receipt.gross == 290.0
        assert receipt.net == 290.0

    def test_fail_receipt_duplicate_nomenclature(self):
        """
        <summary>
        Проверка запрета добавления дублирующейся номенклатуры в строки рецепта
        </summary>
        """
        # Подготовка
        receipt = receipt_model("Тесто")
        row1 = receipt_row_model(self.flour, gross=100.0, net=100.0)
        row2 = receipt_row_model(self.flour, gross=50.0, net=50.0)
        receipt.add_row(row1)

        # Действие и проверка
        with pytest.raises(argument_exception) as exc_info:
            receipt.add_row(row2)

        assert "уже присутствует" in str(exc_info.value)

    def test_fail_receipt_self_inclusion(self):
        """
        <summary>
        Проверка запрета включения технологической карты в саму себя
        </summary>
        """
        # Подготовка
        receipt = receipt_model("Базовый полуфабрикат")
        row = receipt_row_model(receipt=receipt)

        # Действие и проверка
        with pytest.raises(argument_exception) as exc_info:
            receipt.add_row(row)

        assert "в саму себя" in str(exc_info.value)

    def test_success_composite_recursive_receipt_calculation(self):
        """
        <summary>
        Проверка паттерна Composite: рекурсивный расчет массы для составного блюда с полуфабрикатами
        </summary>
        """
        # Подготовка: Полуфабрикат 1 (Тесто)
        dough = receipt_model("Тесто", portions=1, cooking_time=30)
        dough.add_row(receipt_row_model(self.flour, gross=180.0, net=180.0))
        dough.add_row(receipt_row_model(self.water, gross=110.0, net=110.0))

        # Подготовка: Готовое блюдо (Пицца), включающее полуфабрикат и отдельный ингредиент
        pizza = receipt_model("Пицца Маргарита", portions=1, cooking_time=15)
        pizza.add_row(receipt_row_model(receipt=dough))
        pizza.add_row(receipt_row_model(self.cheese, gross=120.0, net=120.0))

        # Действие
        total_gross = pizza.gross
        total_net = pizza.net

        # Проверка
        assert total_gross == 410.0
        assert total_net == 410.0

    def test_fail_composite_cyclic_dependency_detection(self):
        """
        <summary>
        Проверка выявления циклической зависимости между технологическими картами
        </summary>
        """
        # Подготовка: рецепт A и рецепт B
        receipt_a = receipt_model("Техкарта A")
        receipt_b = receipt_model("Техкарта B")

        receipt_a.add_row(receipt_row_model(self.flour, gross=100.0, net=100.0))
        receipt_b.add_row(receipt_row_model(receipt=receipt_a))

        # Создание взаимной ссылки: A ссылается на B, B ссылается на A
        row_cycle = receipt_row_model(receipt=receipt_b)
        receipt_a.add_row(row_cycle)

        # Действие и проверка
        with pytest.raises(operation_exception) as exc_info:
            _ = receipt_a.gross

        assert "циклическая зависимость" in str(exc_info.value)

    # -------------------------------------------------------------------------
    # Тесты интеграции с хранилищем (storage_manager)
    # -------------------------------------------------------------------------

    def test_success_storage_manager_custom_pizza_seed_data(self):
        """
        <summary>
        Проверка первичной загрузки авторской технологической карты пиццы в storage_manager
        </summary>
        """
        # Подготовка
        manager = storage_manager()
        manager.clear()

        # Действие
        manager.first_start()
        pizza = manager.get_receipt("Пицца Пепперони")

        # Проверка
        assert pizza is not None
        assert pizza.name == "Пицца Пепперони"
        assert len(pizza.rows) == 4
        # Тесто (305) + Соус (85) + Сыр (120) + Пепперони (80) = 590.0
        assert pizza.gross == 590.0
        # Тесто (305) + Соус (82) + Сыр (120) + Пепперони (75) = 582.0
        assert pizza.net == 582.0

    def test_fail_storage_manager_duplicate_receipt_registration(self):
        """
        <summary>
        Проверка запрета регистрации дублирующейся технологической карты в storage_manager
        </summary>
        """
        # Подготовка
        manager = storage_manager()
        manager.clear()
        manager.first_start()

        duplicate = receipt_model("Пицца Пепперони")

        # Действие и проверка
        with pytest.raises(operation_exception) as exc_info:
            manager.add_receipt(duplicate)

        assert "уже зарегистрирован" in str(exc_info.value)
