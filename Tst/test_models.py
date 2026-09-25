import pytest
from Src.Core.exception import argument_exception
from Src.Models.range_model import range_model
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.storage_model import storage_model
from Src.Models.organization_model import organization_model
from Src.Models.nomenclature_model import nomenclature_model


def test_success_range_model_creation_default():
    """
    <summary>
    Проверка корректного создания модели единицы измерения по умолчанию.
    Ожидается: коэффициент равен 1, базовая единица указывает на сам объект.
    </summary>
    """
    range_item = range_model("грамм")
    assert range_item.name == "грамм"
    assert range_item.coeff == 1
    assert range_item.base_range == range_item
    assert range_item.id != ""


def test_success_range_model_float_coeff():
    """
    <summary>
    Проверка создания единицы измерения с вещественным коэффициентом пересчета.
    Ожидается: вещественный коэффициент успешно сохраняется.
    </summary>
    """
    gram = range_model("грамм", 1)
    milligram = range_model("миллиграмм", 0.001, gram)
    assert milligram.coeff == 0.001
    assert milligram.base_range == gram


def test_success_range_model_conversion_demo():
    """
    <summary>
    Демонстрация работы с базовой и производной единицами измерения.
    Ожидается: коэффициент 1000 и ссылка на базовую единицу "грамм".
    </summary>
    """
    base_range = range_model("грамм", 1)
    kg_range = range_model("кг", 1000, base_range)

    assert base_range.name == "грамм"
    assert base_range.coeff == 1
    assert base_range.base_range == base_range

    assert kg_range.name == "кг"
    assert kg_range.coeff == 1000
    assert kg_range.base_range == base_range
    assert kg_range.base_range.name == "грамм"

    weight_in_kg = 2.5
    weight_in_base_grams = weight_in_kg * kg_range.coeff
    assert weight_in_base_grams == 2500.0


def test_success_range_model_setters():
    """
    <summary>
    Проверка изменения свойств единицы измерения через сеттеры.
    Ожидается: успешное обновление name, coeff и base_range.
    </summary>
    """
    item = range_model("грамм", 1)
    item.name = "килограмм"
    item.coeff = 1000
    base = range_model("грамм", 1)
    item.base_range = base

    assert item.name == "килограмм"
    assert item.coeff == 1000
    assert item.base_range == base


def test_fail_range_model_invalid_coeff():
    """
    <summary>
    Проверка выброса исключения при некорректном коэффициенте единицы измерения.
    Ожидается: argument_exception при coeff <= 0 или нечисловом типе.
    </summary>
    """
    with pytest.raises(argument_exception):
        range_model("кг", 0)

    with pytest.raises(argument_exception):
        range_model("кг", -5)

    with pytest.raises(argument_exception):
        range_model("кг", "тысяча")


def test_fail_range_model_invalid_base_range():
    """
    <summary>
    Проверка выброса исключения при передаче объекта некорректного типа в base_range.
    Ожидается: argument_exception при значении, отличном от range_model.
    </summary>
    """
    with pytest.raises(argument_exception):
        range_model("кг", 1000, "грамм")


def test_success_nomenclature_group_model_creation():
    """
    <summary>
    Проверка успешного создания группы номенклатуры.
    Ожидается: корректное наименование и сгенерированный id.
    </summary>
    """
    group = nomenclature_group_model("Сырье")
    assert group.name == "Сырье"
    assert group.id != ""


def test_success_storage_model_creation():
    """
    <summary>
    Проверка успешного создания склада.
    Ожидается: корректное наименование и сгенерированный id.
    </summary>
    """
    storage = storage_model("Основной склад")
    assert storage.name == "Основной склад"
    assert storage.id != ""


def test_success_organization_model_creation_10_digits_inn():
    """
    <summary>
    Проверка создания организации с 10-значным ИНН (юрлицо).
    Ожидается: корректная инициализация всех полей организации.
    </summary>
    """
    org = organization_model("Ромашка", "1234567890", "123456789", "12345678901", "ООО")
    assert org.name == "Ромашка"
    assert org.inn == "1234567890"
    assert org.bik == "123456789"
    assert org.account == "12345678901"
    assert org.ownership_form == "ООО"
    assert org.id != ""


def test_success_organization_model_creation_12_digits_inn():
    """
    <summary>
    Проверка создания организации с 12-значным ИНН (ИП).
    Ожидается: успешное сохранение 12-значного ИНН.
    </summary>
    """
    org = organization_model("ИП Иванов", "123456789012", "123456789", "12345678901", "ИП")
    assert org.inn == "123456789012"


def test_success_organization_model_setters():
    """
    <summary>
    Проверка обновления полей организации через свойства-сеттеры.
    Ожидается: успешное обновление inn, bik, account, ownership_form.
    </summary>
    """
    org = organization_model("Организация", "1234567890", "123456789", "12345678901", "ООО")
    org.inn = "987654321012"
    org.bik = "987654321"
    org.account = "98765432109"
    org.ownership_form = "ПАО"

    assert org.inn == "987654321012"
    assert org.bik == "987654321"
    assert org.account == "98765432109"
    assert org.ownership_form == "ПАО"


def test_fail_organization_model_invalid_lengths():
    """
    <summary>
    Проверка выброса исключений при некорректной длине реквизитов организации.
    Ожидается: argument_exception для ИНН!=10/12, БИК!=9, Счета!=11, формы>5.
    </summary>
    """
    with pytest.raises(argument_exception):
        organization_model("Ромашка", "123456789", "123456789", "12345678901", "ООО")

    with pytest.raises(argument_exception):
        organization_model("Ромашка", "12345678901", "123456789", "12345678901", "ООО")

    with pytest.raises(argument_exception):
        organization_model("Ромашка", "1234567890", "12345678", "12345678901", "ООО")

    with pytest.raises(argument_exception):
        organization_model("Ромашка", "1234567890", "1234567890", "12345678901", "ООО")

    with pytest.raises(argument_exception):
        organization_model("Ромашка", "1234567890", "123456789", "1234567890", "ООО")

    with pytest.raises(argument_exception):
        organization_model("Ромашка", "1234567890", "123456789", "123456789012", "ООО")

    with pytest.raises(argument_exception):
        organization_model("Ромашка", "1234567890", "123456789", "12345678901", "СЛИШКОМ_ДЛИННО")


def test_fail_organization_model_non_digit_data():
    """
    <summary>
    Проверка выброса исключения при наличии нецифровых символов в реквизитах.
    Ожидается: argument_exception при наличии букв, дефисов или пробелов внутри цифр.
    </summary>
    """
    with pytest.raises(argument_exception):
        organization_model("Ромашка", "12345abc90", "123456789", "12345678901", "ООО")

    with pytest.raises(argument_exception):
        organization_model("Ромашка", "1234567890", "12345-789", "12345678901", "ООО")

    with pytest.raises(argument_exception):
        organization_model("Ромашка", "1234567890", "123456789", "12345 678901", "ООО")


def test_fail_organization_model_invalid_types():
    """
    <summary>
    Проверка выброса исключений при передаче нестроковых аргументов.
    Ожидается: argument_exception во всех случаях несоответствия типа.
    </summary>
    """
    with pytest.raises(argument_exception):
        organization_model("Ромашка", 1234567890, "123456789", "12345678901", "ООО")

    with pytest.raises(argument_exception):
        organization_model("Ромашка", "1234567890", 123456789, "12345678901", "ООО")

    with pytest.raises(argument_exception):
        organization_model("Ромашка", "1234567890", "123456789", 12345678901, "ООО")

    with pytest.raises(argument_exception):
        organization_model("Ромашка", "1234567890", "123456789", "12345678901", 123)


def test_fail_organization_model_empty_ownership_form():
    """
    <summary>
    Проверка выброса исключения при пустой форме собственности.
    Ожидается: argument_exception при пустой строке или строке из пробелов.
    </summary>
    """
    with pytest.raises(argument_exception):
        organization_model("Ромашка", "1234567890", "123456789", "12345678901", "   ")


def test_success_nomenclature_model_creation():
    """
    <summary>
    Проверка создания номенклатуры со связанной группой и единицей измерения.
    Ожидается: корректное сохранение связей с другими моделями.
    </summary>
    """
    group = nomenclature_group_model("Ингредиенты")
    unit = range_model("кг", 1)
    nom = nomenclature_model("Мука", "Мука пшеничная высший сорт", group, unit)

    assert nom.name == "Мука"
    assert nom.full_name == "Мука пшеничная высший сорт"
    assert nom.group == group
    assert nom.range == unit
    assert nom.id != ""


def test_success_nomenclature_model_setters():
    """
    <summary>
    Проверка обновления свойств номенклатуры через сеттеры.
    Ожидается: корректное обновление всех свойств объекта.
    </summary>
    """
    group1 = nomenclature_group_model("Группа 1")
    group2 = nomenclature_group_model("Группа 2")
    unit1 = range_model("кг", 1)
    unit2 = range_model("грамм", 1)

    nom = nomenclature_model("Сахар", "Сахар белый", group1, unit1)
    nom.name = "Сахар-песок"
    nom.full_name = "Сахар белый свекловичный"
    nom.group = group2
    nom.range = unit2

    assert nom.name == "Сахар-песок"
    assert nom.full_name == "Сахар белый свекловичный"
    assert nom.group == group2
    assert nom.range == unit2


def test_success_nomenclature_model_full_name_length_limit():
    """
    <summary>
    Проверка граничных значений длины полного наименования номенклатуры (до 255 символов).
    Ожидается: 255 символов допустимо, 256 символов вызывает argument_exception.
    </summary>
    """
    group = nomenclature_group_model("Ингредиенты")
    unit = range_model("кг", 1)

    valid_long_name = "А" * 255
    nom = nomenclature_model("Мука", valid_long_name, group, unit)
    assert nom.full_name == valid_long_name

    invalid_long_name = "А" * 256
    with pytest.raises(argument_exception):
        nomenclature_model("Мука", invalid_long_name, group, unit)


def test_fail_nomenclature_model_invalid_full_name():
    """
    <summary>
    Проверка выброса исключения при некорректном full_name номенклатуры.
    Ожидается: argument_exception при нестроковом или пустом значении.
    </summary>
    """
    group = nomenclature_group_model("Ингредиенты")
    unit = range_model("кг", 1)

    with pytest.raises(argument_exception):
        nomenclature_model("Мука", 12345, group, unit)

    with pytest.raises(argument_exception):
        nomenclature_model("Мука", "   ", group, unit)


def test_fail_nomenclature_model_invalid_relations():
    """
    <summary>
    Проверка валидации связанных моделей при создании номенклатуры.
    Ожидается: argument_exception при передаче объектов неверных типов в group и range.
    </summary>
    """
    unit = range_model("кг", 1)
    with pytest.raises(argument_exception):
        nomenclature_model("Мука", "Мука", "не_группа", unit)

    group = nomenclature_group_model("Ингредиенты")
    with pytest.raises(argument_exception):
        nomenclature_model("Мука", "Мука", group, "не_единица")


def test_success_and_fail_abstract_reference_name_limit():
    """
    <summary>
    Проверка ограничения длины поля name (до 50 символов).
    Ожидается: 50 символов допустимо, 51 символ вызывает argument_exception.
    </summary>
    """
    valid_name = "А" * 50
    group = nomenclature_group_model(valid_name)
    assert group.name == valid_name

    invalid_name = "А" * 51
    with pytest.raises(argument_exception):
        nomenclature_group_model(invalid_name)
