"""
Модуль менеджера хранения данных (storage_manager)
Автор: Alexander
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

# Динамическое определение корня репозитория (переносимо для локального запуска, Docker и CI/CD)
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Core.abstract_manager import abstract_manager
from Src.Core.event_type_enum import event_type_enum
from Src.Core.log_level_enum import log_level_enum
from Src.Logics.observer import observer
from Src.Core.abstract_reference import abstract_reference
from Src.Core.validator import validator, argument_exception, operation_exception
from Src.Models.storage_model import storage_model
from Src.Models.range_model import range_model
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.settings_model import settings_model
from Src.Models.receipt_row_model import receipt_row_model
from Src.Models.receipt_model import receipt_model
from Src.Models.transaction_model import transaction_model
import datetime
from Src.Logics.settings_manager import settings_manager


class storage_manager(abstract_manager):
    """
    Менеджер хранения данных доменных моделей на основе прямых реестров (Singleton).
    Обеспечивает доступ за O(1) по id и name, статическую фабрику первичных данных
    и строгий контроль уникальности элементов.
    """

    __instance: Optional["storage_manager"] = None

    def __new__(cls, *args, **kwargs):
        """
        Реализация шаблона Singleton для гарантирования единственного экземпляра хранилища.
        """
        if cls.__instance is None:
            cls.__instance = super(storage_manager, cls).__new__(cls)
        return cls.__instance

    def __init__(self, settings: Optional[settings_model] = None):
        """
        Инициализация менеджера хранения данных.
        Поддерживает как работу без параметров, так и передачу настроек settings_model.
        """
        if getattr(self, "_initialized", False):
            if settings is not None:
                self._settings = settings
            return

        super().__init__()

        self._settings: Optional[settings_model] = settings
        self.__is_first_start: bool = settings.first_start if settings is not None else True

        # Основное хранилище по категориям: category_key -> {id: entity}
        self._data: Dict[str, Dict[str, abstract_reference]] = {
            key: {} for key in self.keys()
        }

        # Вторичный индекс для мгновенного поиска по наименованию: category_key -> {name: id}
        self._name_index: Dict[str, Dict[str, str]] = {
            key: {} for key in self.keys()
        }

        self._initialized = True

    # -------------------------------------------------------------------------
    # Константы ключей категорий хранилища
    # -------------------------------------------------------------------------

    @staticmethod
    def storage_key() -> str:
        """
        Ключ категории складов
        """
        return "storage_key"

    @staticmethod
    def range_key() -> str:
        """
        Ключ категории единиц измерения
        """
        return "range_model"

    @staticmethod
    def group_key() -> str:
        """
        Ключ категории групп номенклатуры
        """
        return "group_model"

    @staticmethod
    def nomenclature_key() -> str:
        """
        Ключ категории номенклатуры
        """
        return "nomenclature_model"

    @staticmethod
    def receipt_key() -> str:
        """
        Ключ категории технологических карт
        """
        return "receipt_model"

    @staticmethod
    def transaction_key() -> str:
        """
        Ключ категории складских транзакций
        """
        return "transaction_model" 

    @staticmethod
    def domains() -> dict:
        """
        Словарь всех зарегистрированных категорий сущностей и их описаний.
        Ключ — наименование категории (например, "nomenclature_model").
        Значение — описание категории из docstring статического метода.
        """
        result = {}
        method_names = [
            name for name in dir(storage_manager)
            if callable(getattr(storage_manager, name)) and name.endswith('_key')
        ]
        for name in method_names:
            method = getattr(storage_manager, name)
            key_val = method()
            doc = method.__doc__
            desc = doc.strip().split('\n')[0] if doc else name
            result[key_val] = desc
        return result

    @staticmethod
    def keys() -> list:
        """
        Получить список всех ключей категорий хранилища
        """
        return list(storage_manager.domains().keys())


    # -------------------------------------------------------------------------
    # Свойства доступа к флагам и данным
    # -------------------------------------------------------------------------

    @property
    def is_first_start(self) -> bool:
        """
        Флаг первого запуска системы
        """
        return self.__is_first_start

    @is_first_start.setter
    def is_first_start(self, value: bool) -> None:
        """
        Сеттер флага первого запуска с валидацией типа
        """
        validator.validate_type(value, bool, field_name="is_first_start")
        self.__is_first_start = value

    @property
    def data(self) -> Dict[str, Any]:
        """
        Набор данных хранилища со списками сущностей по категориям.
        """
        return {
            self.storage_key(): self.storages,
            self.range_key(): self.ranges,
            self.group_key(): self.groups,
            self.nomenclature_key(): self.nomenclatures,
            self.receipt_key(): self.receipts,
            "storage": self._data.get(self.storage_key(), {}),
            "range": self._data.get(self.range_key(), {}),
            "group": self._data.get(self.group_key(), {}),
            "nomenclature": self._data.get(self.nomenclature_key(), {}),
            "receipt": self._data.get(self.receipt_key(), {}),
        }

    @property
    def storages(self) -> List[storage_model]:
        """
        Список всех зарегистрированных складов
        """
        return list(self._data[self.storage_key()].values())

    @property
    def storages_dict(self) -> Dict[str, storage_model]:
        """
        Словарь складов с индексацией по id (O(1) доступ)
        """
        return self._data[self.storage_key()]

    @property
    def ranges(self) -> List[range_model]:
        """
        Список всех зарегистрированных единиц измерения
        """
        return list(self._data[self.range_key()].values())

    @property
    def ranges_dict(self) -> Dict[str, range_model]:
        """
        Словарь единиц измерения с индексацией по id (O(1) доступ)
        """
        return self._data[self.range_key()]

    @property
    def groups(self) -> List[nomenclature_group_model]:
        """
        Список всех зарегистрированных групп номенклатуры
        """
        return list(self._data[self.group_key()].values())

    @property
    def groups_dict(self) -> Dict[str, nomenclature_group_model]:
        """
        Словарь групп номенклатуры с индексацией по id (O(1) доступ)
        """
        return self._data[self.group_key()]

    @property
    def receipts(self) -> List[receipt_model]:
        """
        Список зарегистрированных технологических карт
        """
        return list(self._data[self.receipt_key()].values())

    @property
    def receipts_dict(self) -> Dict[str, receipt_model]:
        """
        Словарь технологических карт с доступом по id
        """
        return self._data[self.receipt_key()]

    @property
    def nomenclatures(self) -> List[nomenclature_model]:
        """
        Список всей зарегистрированной номенклатуры
        """
        return list(self._data[self.nomenclature_key()].values())

    @property
    def nomenclatures_dict(self) -> Dict[str, nomenclature_model]:
        """
        Словарь номенклатуры с индексацией по id (O(1) доступ)
        """
        return self._data[self.nomenclature_key()]

    # -------------------------------------------------------------------------
    # Статическая фабрика начальных данных (Static Seed Factory)
    # -------------------------------------------------------------------------

    @staticmethod
    def create_seed_data() -> Dict[str, List[abstract_reference]]:
        """
        Статическая фабрика создания первичных данных для первого запуска системы.
        Формирует базовый набор складов, единиц измерения, групп номенклатуры,
        ингредиентов и технологических карт.

        Returns:
            Dict[str, List[abstract_reference]]: Словарь списков сущностей по категориям
        """
        # 1. Единицы измерения
        unit_piece = range_model("штука", 1)
        unit_kg = range_model.create_kilogramm()
        unit_gram = unit_kg.base_range
        unit_liter = range_model.create_liter()
        unit_ml = unit_liter.base_range

        ranges_seed = [unit_piece, unit_gram, unit_kg, unit_ml, unit_liter]

        # 2. Склады сети
        storage_main = storage_model("Главный склад", "г. Красноярск, ул. Ленина, д. 1")
        storage_factory = storage_model("Производственный цех", "г. Красноярск, пр. Мира, д. 82")
        storage_store = storage_model("Склад ресторана №1", "г. Красноярск, ул. Маркса, д. 45")

        storages_seed = [storage_main, storage_factory, storage_store]

        # 3. Группы номенклатуры
        group_grocery = nomenclature_group_model("Сырье и бакалея")
        group_dairy = nomenclature_group_model("Молочная продукция")
        group_semi = nomenclature_group_model("Полуфабрикаты")
        group_dishes = nomenclature_group_model("Готовая продукция")

        groups_seed = [group_grocery, group_dairy, group_semi, group_dishes]

        # 4. Базовая номенклатура
        nom_flour = nomenclature_model(
            name="Мука пшеничная",
            full_name="Мука пшеничная хлебопекарная высший сорт",
            group=group_grocery,
            range=unit_gram,
        )
        nom_sugar = nomenclature_model(
            name="Сахар",
            full_name="Сахар белый кристаллический свекловичный",
            group=group_grocery,
            range=unit_gram,
        )
        nom_butter = nomenclature_model(
            name="Сливочное масло",
            full_name="Масло сливочное крестьянское 82.5% ГОСТ",
            group=group_dairy,
            range=unit_gram,
        )
        nom_egg = nomenclature_model(
            name="Яйцо куриное",
            full_name="Яйцо куриное столовое пищевое категории С0",
            group=group_grocery,
            range=unit_piece,
        )
        nom_milk = nomenclature_model(
            name="Молоко",
            full_name="Молоко пастеризованное питьевое 3.2%",
            group=group_dairy,
            range=unit_ml,
        )
        nom_vanilla = nomenclature_model(
            name="Ванилин",
            full_name="Ванилин пищевой ароматический кристаллический",
            group=group_grocery,
            range=unit_gram,
        )
        nom_waffle = nomenclature_model(
            name="Вафли хрустящие",
            full_name="Вафли венские хрустящие классические порционные",
            group=group_dishes,
            range=unit_piece,
        )

        # Номенклатура для авторской технологической карты «Пицца Пепперони»
        nom_water = nomenclature_model(
            name="Вода питьевая",
            full_name="Вода питьевая очищенная",
            group=group_grocery,
            range=unit_ml,
        )
        nom_olive_oil = nomenclature_model(
            name="Масло оливковое",
            full_name="Масло оливковое нерафинированное Extra Virgin",
            group=group_grocery,
            range=unit_gram,
        )
        nom_yeast = nomenclature_model(
            name="Дрожжи сухие",
            full_name="Дрожжи хлебопекарные сухие инстантные",
            group=group_grocery,
            range=unit_gram,
        )
        nom_salt = nomenclature_model(
            name="Соль пищевая",
            full_name="Соль поваренная пищевая выварочная",
            group=group_grocery,
            range=unit_gram,
        )
        nom_tomatoes = nomenclature_model(
            name="Томаты протертые",
            full_name="Томаты протертые консервированные",
            group=group_grocery,
            range=unit_gram,
        )
        nom_garlic = nomenclature_model(
            name="Чеснок свежий",
            full_name="Чеснок свежий урожай",
            group=group_grocery,
            range=unit_gram,
        )
        nom_basil = nomenclature_model(
            name="Базилик сушеный",
            full_name="Базилик сушеный измельченный",
            group=group_grocery,
            range=unit_gram,
        )
        nom_mozzarella = nomenclature_model(
            name="Сыр Моцарелла",
            full_name="Сыр Моцарелла для пиццы 45%",
            group=group_dairy,
            range=unit_gram,
        )
        nom_pepperoni = nomenclature_model(
            name="Колбаски Пепперони",
            full_name="Колбаски сырокопченые Пепперони острые",
            group=group_grocery,
            range=unit_gram,
        )
        nom_dough = nomenclature_model(
            name="Тесто для пиццы",
            full_name="Тесто дрожжевое для пиццы порционное",
            group=group_semi,
            range=unit_piece,
        )
        nom_sauce = nomenclature_model(
            name="Соус томатный фирменный",
            full_name="Соус томатный фирменный для пиццы",
            group=group_semi,
            range=unit_gram,
        )
        nom_pizza = nomenclature_model(
            name="Пицца Пепперони",
            full_name="Пицца Пепперони 30 см традиционное тесто",
            group=group_dishes,
            range=unit_piece,
        )

        nomenclatures_seed = [
            nom_flour,
            nom_sugar,
            nom_butter,
            nom_egg,
            nom_milk,
            nom_vanilla,
            nom_waffle,
            nom_water,
            nom_olive_oil,
            nom_yeast,
            nom_salt,
            nom_tomatoes,
            nom_garlic,
            nom_basil,
            nom_mozzarella,
            nom_pepperoni,
            nom_dough,
            nom_sauce,
            nom_pizza,
        ]

        # 5. Технологические карты (составные рецепты)
        receipt_dough = receipt_model(
            name="Тесто для пиццы",
            portions=1,
            cooking_time=60,
            rows=[
                receipt_row_model(nom_flour, gross=180, net=180, range=unit_gram),
                receipt_row_model(nom_water, gross=110, net=110, range=unit_ml),
                receipt_row_model(nom_olive_oil, gross=10, net=10, range=unit_gram),
                receipt_row_model(nom_yeast, gross=3, net=3, range=unit_gram),
                receipt_row_model(nom_salt, gross=2, net=2, range=unit_gram),
            ],
        )

        receipt_sauce = receipt_model(
            name="Соус томатный фирменный",
            portions=1,
            cooking_time=15,
            rows=[
                receipt_row_model(nom_tomatoes, gross=70, net=70, range=unit_gram),
                receipt_row_model(nom_garlic, gross=8, net=5, range=unit_gram),
                receipt_row_model(nom_olive_oil, gross=5, net=5, range=unit_gram),
                receipt_row_model(nom_basil, gross=2, net=2, range=unit_gram),
            ],
        )

        receipt_pizza = receipt_model(
            name="Пицца Пепперони",
            portions=1,
            cooking_time=15,
            rows=[
                receipt_row_model(nomenclature=nom_dough, receipt=receipt_dough),
                receipt_row_model(nomenclature=nom_sauce, receipt=receipt_sauce),
                receipt_row_model(nom_mozzarella, gross=120, net=120, range=unit_gram),
                receipt_row_model(nom_pepperoni, gross=80, net=75, range=unit_gram),
            ],
        )

        receipts_seed = [receipt_dough, receipt_sauce, receipt_pizza]

        # 6. Складские транзакции (движения товаров)
        tx_flour_1 = transaction_model(
            name="Поступление муки",
            storage=storage_main,
            nomenclature=nom_flour,
            range_item=unit_gram,
            value=50000.0,
            period=datetime.datetime(2026, 11, 1, 9, 0, 0),
        )
        tx_flour_2 = transaction_model(
            name="Расход муки на выпечку",
            storage=storage_main,
            nomenclature=nom_flour,
            range_item=unit_gram,
            value=-12000.0,
            period=datetime.datetime(2026, 11, 10, 14, 0, 0),
        )
        tx_sugar_1 = transaction_model(
            name="Поступление сахара",
            storage=storage_main,
            nomenclature=nom_sugar,
            range_item=unit_gram,
            value=20000.0,
            period=datetime.datetime(2026, 11, 2, 10, 30, 0),
        )
        tx_sugar_2 = transaction_model(
            name="Списание сахара",
            storage=storage_main,
            nomenclature=nom_sugar,
            range_item=unit_gram,
            value=-5000.0,
            period=datetime.datetime(2026, 11, 12, 16, 0, 0),
        )
        tx_butter_1 = transaction_model(
            name="Поступление масла",
            storage=storage_main,
            nomenclature=nom_butter,
            range_item=unit_gram,
            value=15000.0,
            period=datetime.datetime(2026, 11, 3, 11, 0, 0),
        )
        tx_eggs_1 = transaction_model(
            name="Поступление яиц",
            storage=storage_main,
            nomenclature=nom_egg,
            range_item=unit_piece,
            value=300.0,
            period=datetime.datetime(2026, 11, 4, 8, 30, 0),
        )
        transactions_seed = [tx_flour_1, tx_flour_2, tx_sugar_1, tx_sugar_2, tx_butter_1, tx_eggs_1]

        return {
            storage_manager.range_key(): ranges_seed,
            storage_manager.storage_key(): storages_seed,
            storage_manager.group_key(): groups_seed,
            storage_manager.nomenclature_key(): nomenclatures_seed,
            storage_manager.receipt_key(): receipts_seed,
            storage_manager.transaction_key(): transactions_seed,
        }

    # -------------------------------------------------------------------------
    # Регистрация и контроль уникальности (O(1))
    # -------------------------------------------------------------------------

    def _register_item(
        self,
        category_key: str,
        item: abstract_reference,
        expected_type: Type[abstract_reference],
    ) -> None:
        """
        Регистрация сущности в реестре с проверкой типа и гарантии уникальности по id и name за O(1).

        Args:
            category_key (str): Ключ категории хранилища
            item (abstract_reference): Добавляемая модель
            expected_type (Type[abstract_reference]): Ожидаемый тип модели

        Raises:
            argument_exception: При передаче некорректного типа объекта
            operation_exception: При обнаружении дубликата по id или name
        """
        validator.validate_type(item, expected_type, field_name=category_key)

        item_id = item.id
        item_name = item.name

        # Проверка уникальности по идентификатору за O(1)
        if item_id in self._data[category_key]:
            msg = f"Ошибка добавления: элемент с id='{item_id}' уже существует в категории '{category_key}'!"
            observer().notify(
                event_type_enum.STORAGE_ERROR,
                {"subsystem": "storage_manager", "level": log_level_enum.ERROR, "message": msg},
            )
            raise operation_exception(msg)

        # Проверка уникальности по наименованию за O(1)
        if item_name in self._name_index[category_key]:
            msg = f"Ошибка добавления: элемент с наименованием '{item_name}' уже зарегистрирован в категории '{category_key}'!"
            observer().notify(
                event_type_enum.STORAGE_ERROR,
                {"subsystem": "storage_manager", "level": log_level_enum.ERROR, "message": msg},
            )
            raise operation_exception(msg)

        # Регистрация в основном реестре и вторичном индексе
        self._data[category_key][item_id] = item
        self._name_index[category_key][item_name] = item_id

    def _notify_entity_added(self, category_key: str, item: abstract_reference) -> None:
        """
        Оповестить наблюдателей о регистрации сущности или складской транзакции
        """
        if category_key == self.transaction_key() and isinstance(item, transaction_model):
            storage_name = item.storage.name if item.storage else "-"
            nom_name = item.nomenclature.name if item.nomenclature else "-"
            observer().notify(
                event_type_enum.TRANSACTION_CREATED,
                {
                    "subsystem": "warehouse",
                    "level": log_level_enum.INFO,
                    "message": (
                        f"Проведена транзакция id={item.id}: склад='{storage_name}', "
                        f"номенклатура='{nom_name}', объем={item.value}"
                    ),
                },
            )
            return

        observer().notify(
            event_type_enum.ADD_ENTITY,
            {
                "subsystem": "storage_manager",
                "level": log_level_enum.INFO,
                "message": f"Добавлена сущность в категорию '{category_key}': id={item.id}, name='{item.name}'",
            },
        )

    def add_storage(self, item: storage_model) -> None:
        """
        Добавить склад в хранилище с проверкой уникальности
        """
        self._register_item(self.storage_key(), item, storage_model)
        self._notify_entity_added(self.storage_key(), item)

    def add_range(self, item: range_model) -> None:
        """
        Добавить единицу измерения в хранилище с проверкой уникальности
        """
        self._register_item(self.range_key(), item, range_model)
        self._notify_entity_added(self.range_key(), item)

    def add_group(self, item: nomenclature_group_model) -> None:
        """
        Добавить группу номенклатуры в хранилище с проверкой уникальности
        """
        self._register_item(self.group_key(), item, nomenclature_group_model)
        self._notify_entity_added(self.group_key(), item)

    def add_nomenclature(self, item: nomenclature_model) -> None:
        """
        Добавить номенклатуру в хранилище с проверкой уникальности
        """
        self._register_item(self.nomenclature_key(), item, nomenclature_model)
        self._notify_entity_added(self.nomenclature_key(), item)

    def add_receipt(self, item: receipt_model) -> None:
        """
        Добавить технологическую карту в хранилище с проверкой уникальности
        """
        self._register_item(self.receipt_key(), item, receipt_model)
        self._notify_entity_added(self.receipt_key(), item)

    def add_transaction(self, item: transaction_model) -> None:
        """
        Добавить складскую транзакцию в хранилище
        """
        validator.validate(item, transaction_model, field_name="transaction")
        self._register_item(self.transaction_key(), item, transaction_model)
        self._notify_entity_added(self.transaction_key(), item)

    @property
    def transactions(self) -> List[transaction_model]:
        """
        Список всех зарегистрированных складских транзакций
        """
        return list(self._data.get(self.transaction_key(), {}).values())

    # -------------------------------------------------------------------------
    # Быстрый поиск за O(1) по id и наименованию
    # -------------------------------------------------------------------------

    def get_by_id(self, category_key: str, item_id: str) -> Optional[abstract_reference]:
        """
        Поиск элемента по уникальному id за O(1)
        """
        validator.validate_type(category_key, str, field_name="category_key")
        validator.validate_type(item_id, str, field_name="item_id")
        return self._data.get(category_key, {}).get(item_id)

    def get_by_name(self, category_key: str, name: str) -> Optional[abstract_reference]:
        """
        Поиск элемента по наименованию за O(1) через вторичный индекс
        """
        validator.validate_type(category_key, str, field_name="category_key")
        validator.validate_type(name, str, field_name="name")
        item_id = self._name_index.get(category_key, {}).get(name.strip())
        if item_id is None:
            return None
        return self._data.get(category_key, {}).get(item_id)

    def get_storage(self, identifier: str) -> Optional[storage_model]:
        """
        Поиск склада по id или наименованию за O(1)
        """
        return self.get_by_id(self.storage_key(), identifier) or self.get_by_name(self.storage_key(), identifier)

    def get_range(self, identifier: str) -> Optional[range_model]:
        """
        Поиск единицы измерения по id или наименованию за O(1)
        """
        return self.get_by_id(self.range_key(), identifier) or self.get_by_name(self.range_key(), identifier)

    def get_group(self, identifier: str) -> Optional[nomenclature_group_model]:
        """
        Поиск группы номенклатуры по id или наименованию за O(1)
        """
        return self.get_by_id(self.group_key(), identifier) or self.get_by_name(self.group_key(), identifier)

    def get_nomenclature(self, identifier: str) -> Optional[nomenclature_model]:
        """
        Поиск номенклатуры по id или наименованию за O(1)
        """
        return self.get_by_id(self.nomenclature_key(), identifier) or self.get_by_name(self.nomenclature_key(), identifier)

    def get_receipt(self, identifier: str) -> Optional[receipt_model]:
        """
        Поиск технологической карты по id или наименованию за O(1)
        """
        return self.get_by_id(self.receipt_key(), identifier) or self.get_by_name(self.receipt_key(), identifier)

    def resolve_category(self, entity_type: str) -> Optional[str]:
        """
        Разрешение наименования типа сущности в ключ категории хранилища
        """
        if not isinstance(entity_type, str):
            return None
        normalized = entity_type.strip().lower()
        for key in self.keys():
            clean_key = key.lower().replace("_model", "").replace("_key", "")
            if normalized == key.lower() or normalized == clean_key:
                return key
        return None

    def get_by_type_and_id(self, entity_type: str, identifier: str) -> Optional[abstract_reference]:
        """
        Полиморфный поиск сущности в хранилище по ее типу и идентификатору или наименованию за O(1)
        """
        category_key = self.resolve_category(entity_type)
        if not category_key:
            return None
        return self.get_by_id(category_key, identifier) or self.get_by_name(category_key, identifier)

    @classmethod
    def get_model_type(cls, category_key: str) -> Optional[Type[abstract_reference]]:
        """
        Динамическое определение типа модели через рефлексию подклассов abstract_reference
        """
        resolved = cls().resolve_category(category_key)
        if not resolved:
            return None

        token = resolved.lower().replace("_model", "").replace("_key", "")
        expected_names = {resolved.lower(), f"{token}_model", f"nomenclature_{token}_model"}
        for model_cls in abstract_reference.__subclasses__():
            if model_cls.__name__.lower() in expected_names:
                return model_cls
        return None

    def get_all(self, category_key: str) -> List[abstract_reference]:
        """
        Получить список всех сущностей указанной категории
        """
        resolved = self.resolve_category(category_key)
        if not resolved or resolved not in self._data:
            return []
        return list(self._data[resolved].values())

    def can_delete(self, category_key: str, identifier: str) -> tuple[bool, str]:
        """
        Проверка ссылочной целостности через специализированный сервис reference_service (SRP)
        """
        from Src.Logics.reference_service import reference_service

        resolved = self.resolve_category(category_key)
        if not resolved:
            return False, f"Категория '{category_key}' не найдена"

        entity = self.get_by_id(resolved, identifier) or self.get_by_name(resolved, identifier)
        if not entity:
            return False, f"Элемент '{identifier}' не найден в категории '{resolved}'"

        return reference_service(self).can_delete(entity.id)

    def delete(self, category_key: str, identifier: str) -> bool:
        """
        Удаление сущности из хранилища с гарантией ссылочной целостности
        """
        resolved = self.resolve_category(category_key)
        if not resolved:
            msg = f"Категория '{category_key}' не зарегистрирована в хранилище!"
            observer().notify(
                event_type_enum.STORAGE_ERROR,
                {"subsystem": "storage_manager", "level": log_level_enum.ERROR, "message": msg},
            )
            raise operation_exception(msg)

        allowed, reason = self.can_delete(resolved, identifier)
        if not allowed:
            observer().notify(
                event_type_enum.STORAGE_ERROR,
                {"subsystem": "storage_manager", "level": log_level_enum.ERROR, "message": reason},
            )
            raise operation_exception(reason)

        entity = self.get_by_id(resolved, identifier) or self.get_by_name(resolved, identifier)
        if not entity:
            msg = f"Элемент '{identifier}' не найден в категории '{resolved}'!"
            observer().notify(
                event_type_enum.STORAGE_ERROR,
                {"subsystem": "storage_manager", "level": log_level_enum.ERROR, "message": msg},
            )
            raise operation_exception(msg)

        del self._data[resolved][entity.id]
        if entity.name in self._name_index[resolved]:
            del self._name_index[resolved][entity.name]

        observer().notify(
            event_type_enum.DELETE_ENTITY,
            {
                "subsystem": "storage_manager",
                "level": log_level_enum.INFO,
                "message": f"Удалена сущность из категории '{resolved}': id={entity.id}, name='{entity.name}'",
            },
        )
        return True

    def add(self, category_key: str, item: abstract_reference) -> None:
        """
        Полиморфное добавление сущности в указанную категорию хранилища
        """
        resolved = self.resolve_category(category_key)
        if not resolved:
            msg = f"Категория '{category_key}' не зарегистрирована в хранилище!"
            observer().notify(
                event_type_enum.STORAGE_ERROR,
                {"subsystem": "storage_manager", "level": log_level_enum.ERROR, "message": msg},
            )
            raise operation_exception(msg)
        expected_type = self.get_model_type(resolved)
        self._register_item(resolved, item, expected_type)
        self._notify_entity_added(resolved, item)

    def update(self, category_key: str, identifier: str, new_item: abstract_reference) -> None:
        """
        Обновление сущности в хранилище с контролем целостности и уникальности
        """
        resolved = self.resolve_category(category_key)
        if not resolved:
            msg = f"Категория '{category_key}' не зарегистрирована в хранилище!"
            observer().notify(
                event_type_enum.STORAGE_ERROR,
                {"subsystem": "storage_manager", "level": log_level_enum.ERROR, "message": msg},
            )
            raise operation_exception(msg)

        entity = self.get_by_id(resolved, identifier) or self.get_by_name(resolved, identifier)
        if not entity:
            msg = f"Элемент '{identifier}' не найден в категории '{resolved}'!"
            observer().notify(
                event_type_enum.STORAGE_ERROR,
                {"subsystem": "storage_manager", "level": log_level_enum.ERROR, "message": msg},
            )
            raise operation_exception(msg)

        if new_item.id != entity.id:
            allowed, reason = self.can_delete(resolved, identifier)
            if not allowed:
                msg = f"Запрещено изменять код (id) сущности, так как {reason}"
                observer().notify(
                    event_type_enum.STORAGE_ERROR,
                    {"subsystem": "storage_manager", "level": log_level_enum.ERROR, "message": msg},
                )
                raise operation_exception(msg)

        if new_item.name != entity.name:
            if new_item.name in self._name_index[resolved]:
                msg = f"Элемент с наименованием '{new_item.name}' уже зарегистрирован!"
                observer().notify(
                    event_type_enum.STORAGE_ERROR,
                    {"subsystem": "storage_manager", "level": log_level_enum.ERROR, "message": msg},
                )
                raise operation_exception(msg)

        del self._data[resolved][entity.id]
        if entity.name in self._name_index[resolved]:
            del self._name_index[resolved][entity.name]

        expected_type = self.get_model_type(resolved)
        self._register_item(resolved, new_item, expected_type)
        observer().notify(
            event_type_enum.UPDATE_ENTITY,
            {
                "subsystem": "storage_manager",
                "level": log_level_enum.INFO,
                "message": f"Обновлена сущность в категории '{resolved}': id={new_item.id}, name='{new_item.name}'",
            },
        )

    # -------------------------------------------------------------------------
    # Логика загрузки, конвертации и первого старта
    # -------------------------------------------------------------------------


    def build(self) -> bool:
        """
        Формирование первичных данных при первом старте.
        """
        first_start_flag = self._settings.first_start if getattr(self, "_settings", None) is not None else self.__is_first_start
        if not first_start_flag or self.is_loaded:
            return False

        self.first_start()
        return True

    def first_start(self) -> None:
        """
        Выполнение логики первого старта системы: наполнение хранилища первичными данными
        (склады, единицы измерения, группы, ингредиенты и блюдо рецепта).
        """
        category_types: Dict[str, Type[abstract_reference]] = {
            self.storage_key(): storage_model,
            self.range_key(): range_model,
            self.group_key(): nomenclature_group_model,
            self.nomenclature_key(): nomenclature_model,
            self.receipt_key(): receipt_model,
            self.transaction_key(): transaction_model,
        }
        seed_data = self.create_seed_data()
        total_items = 0
        for category, items in seed_data.items():
            expected_type = category_types.get(category)
            if expected_type is None:
                continue
            for item in items:
                self._register_item(category, item, expected_type)
                total_items += 1

        self.is_first_start = False
        self.is_loaded = True
        observer().notify(
            event_type_enum.STORAGE_LOADED,
            {
                "subsystem": "storage_manager",
                "level": log_level_enum.INFO,
                "message": f"Хранилище инициализировано: категорий={len(seed_data)}, записей={total_items}",
            },
        )

    def convert(self, is_first: Optional[bool] = None) -> bool:
        """
        Переопределение метода конвертации данных абстрактного менеджера.
        При флаге первого запуска формирует первичный набор сущностей в хранилище.

        Args:
            is_first (Optional[bool]): Флаг принудительного первого запуска

        Returns:
            bool: Результат конвертации данных
        """
        if is_first is not None:
            validator.validate_type(is_first, bool, field_name="is_first")
            flag = is_first
        else:
            flag = self.is_first_start

        if flag:
            self.first_start()
            return True

        return len(self.storages) > 0 or len(self.ranges) > 0

    def load(self, file_name: str = "") -> None:
        """
        Загрузка данных менеджера хранилища.
        При указании несуществующего пути генерирует исключение operation_exception.
        При пустом пути выполняет инициализацию первичных данных или связывание с настройками.

        Args:
            file_name (str): Путь к файлу конфигурации/данных
        """
        validator.validate_type(file_name, str, field_name="file_name")
        clean_path = file_name.strip()

        if clean_path:
            target_path = Path(clean_path)
            if not target_path.is_file():
                self.is_loaded = False
                msg = f"Файл данных не найден: {clean_path}"
                observer().notify(
                    event_type_enum.STORAGE_ERROR,
                    {"subsystem": "storage_manager", "level": log_level_enum.ERROR, "message": msg},
                )
                raise operation_exception(msg)
            self._file_name = str(target_path)
            self.is_loaded = self.convert()
        else:
            self.is_loaded = self.convert()

    def load_from_settings(self, settings_mgr: Optional[settings_manager] = None) -> None:
        """
        Связывание хранилища с менеджером настроек settings_manager
        """
        mgr = settings_mgr if settings_mgr is not None else settings_manager()
        if not mgr.is_loaded:
            try:
                mgr.load()
            except Exception:
                pass
        self.is_loaded = self.convert()

    def clear(self) -> None:
        """
        Полная очистка реестров хранилища и вторичных индексов.
        Используется для сброса состояния между тестами.
        """
        for key in self._data:
            self._data[key].clear()
            self._name_index[key].clear()
        self.is_loaded = False
        self.__is_first_start = True

    @classmethod
    def reset_instance(cls) -> None:
        """
        Полный сброс экземпляра Singleton (для изолированных тестов)
        """
        if cls.__instance is not None:
            cls.__instance.clear()
        cls.__instance = None
