# Архитектурные UML-диаграммы классов: settings_manager и storage_manager

**Автор:** Alexander  
**Проект:** Информационная система ресторанной сети «Ромашка»  
**Паттерны проектирования:** Singleton, Registry, Static Factory Method, Centralized Validator  
**Кандидат:** Candidate 1 — Direct Registry Storage & Static Seed Factory  

---

## 1. Концептуальный обзор архитектуры

Подсистема управления конфигурацией и доменными данными ресторана построена на базе общей иерархии менеджеров `abstract_manager`.
Для обеспечения целостности данных, разделения глобального состояния и гарантии отсутствия дублирования в памяти применяются:
1. **Шаблон Singleton (Одиночка):** Классы `settings_manager` и `storage_manager` реализуют контролируемое создание единственного экземпляра через переопределение метода `__new__`.
2. **Шаблон Registry (Реестр):** Класс `storage_manager` служит центральным типизированным хранилищем доменных моделей (`storage_model`, `range_model`, `nomenclature_group_model`, `nomenclature_model`), поддерживая мгновенный доступ за время $O(1)$ по первичному суррогатному ключу `id` и бизнес-наименованию `name`.
3. **Шаблон Static Factory Method (Статическая фабрика данных):** Метод `storage_manager.create_seed_data()` инкапсулирует алгоритм конструирования нормализованного первичного графа объектов (рецептура венских вафель, склады и единицы измерения) без побочных эффектов.
4. **Централизованный валидатор контрактов:** Класс `validator` гарантирует строгое соблюдение инвариантов типов, ограничений по длине и защиту от классических ловушек Python (включая bool-as-int и IEEE 754 NaN/Inf).

---

## 2. Диаграмма классов storage_manager и доменных моделей

```mermaid
classDiagram
    direction TB

    class abstract_manager {
        <<abstract>>
        #_file_name: str
        #_is_loaded: bool
        #_data: Any
        +load(file_name: str) void
        +convert() bool
        +is_loaded() bool
        +is_loaded(value: bool) void
    }

    class storage_manager {
        -storage_manager __instance$
        -bool __is_first_start
        -_data: Dict~str, Dict~str, abstract_reference~~
        -_name_index: Dict~str, Dict~str, str~~
        +__new__(cls) storage_manager$
        +__init__() void
        +storage_key() str$
        +range_key() str$
        +group_key() str$
        +nomenclature_key() str$
        +is_first_start: bool
        +data: Dict
        +storages: List~storage_model~
        +storages_dict: Dict~str, storage_model~
        +ranges: List~range_model~
        +ranges_dict: Dict~str, range_model~
        +groups: List~nomenclature_group_model~
        +groups_dict: Dict~str, nomenclature_group_model~
        +nomenclatures: List~nomenclature_model~
        +nomenclatures_dict: Dict~str, nomenclature_model~
        +create_seed_data() Dict$
        -_register_item(category_key, item, expected_type) void
        +add_storage(item: storage_model) void
        +add_range(item: range_model) void
        +add_group(item: nomenclature_group_model) void
        +add_nomenclature(item: nomenclature_model) void
        +get_by_id(category_key, item_id) abstract_reference
        +get_by_name(category_key, name) abstract_reference
        +get_storage(identifier: str) storage_model
        +get_range(identifier: str) range_model
        +get_group(identifier: str) nomenclature_group_model
        +get_nomenclature(identifier: str) nomenclature_model
        +first_start() void
        +convert(is_first: bool) bool
        +load(file_name: str) void
        +load_from_settings(settings_mgr: settings_manager) void
        +clear() void
        +reset_instance() void$
    }

    class abstract_reference {
        <<abstract>>
        -__id: UUID
        -__name: str
        +id: str
        +name: str
        +__eq__(value: Any) bool
    }

    class storage_model {
        -__address: str
        +address: str
    }

    class range_model {
        -__coeff: int|float
        -__base_range: range_model
        +coeff: int|float
        +base_range: range_model
    }

    class nomenclature_group_model {
    }

    class nomenclature_model {
        -__full_name: str
        -__group: nomenclature_group_model
        -__range: range_model
        +full_name: str
        +group: nomenclature_group_model
        +range: range_model
    }

    class validator {
        <<utility>>
        +validate(value, type_, len_, field_name, strip)$ bool
        +validate_type(value, type_, field_name)$ bool
        +validate_string(value, min_len, max_len, allow_empty, field_name)$ bool
        +validate_number(value, min_val, max_val, positive_only, field_name)$ bool
        +validate_digits(value, length, allowed_lengths, field_name)$ bool
    }

    abstract_manager <|-- storage_manager : Наследование
    abstract_reference <|-- storage_model : Наследование
    abstract_reference <|-- range_model : Наследование
    abstract_reference <|-- nomenclature_group_model : Наследование
    abstract_reference <|-- nomenclature_model : Наследование

    storage_manager o-- storage_model : Реестр складов
    storage_manager o-- range_model : Реестр единиц измерения
    storage_manager o-- nomenclature_group_model : Реестр групп
    storage_manager o-- nomenclature_model : Реестр номенклатуры

    range_model o-- range_model : Базовая единица
    nomenclature_model --> nomenclature_group_model : Группа
    nomenclature_model --> range_model : Единица измерения

    storage_manager ..> validator : Валидация контрактов
    abstract_reference ..> validator : Проверка полей id/name
```

---

## 3. Диаграмма классов settings_manager и моделей настроек

```mermaid
classDiagram
    direction TB

    class abstract_manager {
        <<abstract>>
        #_file_name: str
        #_is_loaded: bool
        #_data: Any
        +load(file_name: str) void
        +convert() bool
        +is_loaded() bool
    }

    class settings_manager {
        -settings_manager __instance$
        -str __default_file_name
        -settings_model __settings
        +__new__(cls) settings_manager$
        +__init__() void
        -_resolve_file_path(file_name: str) Path
        +load(file_name: str) void
        +convert() bool
        +settings: settings_model
    }

    class settings_model {
        -organization_model __company
        -str __boss_name
        -str __account_name
        +company: organization_model
        +organization: organization_model
        +boss_name: str
        +account_name: str
    }

    class organization_model {
        -str __inn
        -str __bik
        -str __account
        -str __ownership_form
        +inn: str
        +bik: str
        +account: str
        +ownership_form: str
    }

    class abstract_reference {
        <<abstract>>
        +id: str
        +name: str
    }

    abstract_manager <|-- settings_manager : Наследование
    abstract_reference <|-- settings_model : Наследование
    abstract_reference <|-- organization_model : Наследование

    settings_manager *-- settings_model : Управляет
    settings_model *-- organization_model : Содержит реквизиты
    settings_manager ..> storage_manager : Связывание при старте
```

---

## 4. Диаграмма последовательности: Инициализация первичных данных (First Start)

```mermaid
sequenceDiagram
    autonumber
    actor Client as Клиентский код
    participant SM as storage_manager (Singleton)
    participant Factory as Static Seed Factory
    participant Reg as Реестры хранилища (_data & _name_index)
    participant Val as validator

    Client->>SM: convert(is_first=True)
    activate SM
    SM->>Val: validate_type(True, bool)
    Val-->>SM: OK
    SM->>SM: first_start()
    SM->>Factory: storage_manager.create_seed_data()
    activate Factory
    Note over Factory: Создание складов, единиц, групп и номенклатуры рецепта «Вафли хрустящие»
    Factory-->>SM: Dict[category, List[abstract_reference]]
    deactivate Factory

    loop Для каждой категории и сущности
        SM->>SM: _register_item(category_key, item, expected_type)
        SM->>Val: validate_type(item, expected_type)
        Val-->>SM: OK
        SM->>Reg: Проверка id в _data[cat] (O(1))
        Reg-->>SM: Отсутствует (уникален)
        SM->>Reg: Проверка name в _name_index[cat] (O(1))
        Reg-->>SM: Отсутствует (уникален)
        SM->>Reg: Запись в _data[cat][item.id] = item
        SM->>Reg: Запись в _name_index[cat][item.name] = item.id
    end

    SM->>SM: is_first_start = False
    SM->>SM: is_loaded = True
    SM-->>Client: True (успех)
    deactivate SM

    Client->>SM: get_nomenclature("Вафли хрустящие")
    activate SM
    SM->>Reg: Поиск в _name_index["nomenclature"]["Вафли хрустящие"]
    Reg-->>SM: Возврат item_id
    SM->>Reg: Чтение _data["nomenclature"][item_id]
    Reg-->>SM: Объект nomenclature_model
    SM-->>Client: Экземпляр номенклатуры (O(1))
    deactivate SM
```

---

## 5. Описание ключевых связей и контрактов

1. **`storage_manager` и `abstract_manager`:** Наследование с перегрузкой виртуальных методов `load()` и `convert()`. Позволяет использовать полиморфную логику загрузчиков в соответствии с принципом подстановки Лисков (LSP).
2. **`storage_manager` и `storage_model` / `range_model` / `nomenclature_group_model` / `nomenclature_model`:** Отношение ассоциации и агрегации (коллекции объектов находятся в оперативной памяти менеджера, время жизни контролируется процессом приложения).
3. **Хранение в виде `Dict[str, Dict[str, abstract_reference]]`:** Каждая сущность сохраняется с ключом `id`, а вторичный словарь `_name_index` сохраняет проекцию `name -> id`. Это гарантирует отсутствие полных сканирований коллекций при выборках.
4. **Валидация уникальности:** При вызове методов добавления `add_*` проверяется как суррогатный ключ `id`, так и естественный бизнес-ключ `name`. При обнаружении дубликата выбрасывается `operation_exception`.
