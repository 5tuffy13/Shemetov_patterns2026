import sys
from pathlib import Path
from flask import Flask, jsonify, request

repo_root = Path(__file__).resolve().parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Core.exception import operation_exception
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.convertor import convertor
from Src.Logics.report_factory import report_factory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager

# Подключение Connexion и Swagger UI
try:
    import connexion
    connexion_app = connexion.FlaskApp(__name__, specification_dir=str(repo_root))
    connexion_app.add_api("openapi.yaml", arguments={"title": "Patterns 2026 REST API"})
    app = connexion_app.app
except Exception:
    app = Flask(__name__)

# Инициализация синглтонов хранилища, настроек и конвертора
settings = settings_manager()
try:
    settings.load()
except Exception:
    pass

storage = storage_manager()
storage.first_start()
factory = report_factory(settings)
conv = convertor()


# -----------------------------------------------------------------------------
# Эндпоинты форматов и отчетов
# -----------------------------------------------------------------------------


@app.route("/api/reports/formats", methods=["GET"])
def get_reports_formats():
    """
    Получить перечень форматов отчетов в формате JSON
    """
    formats = [item.name for item in report_type_enum]
    return jsonify(formats), 200


@app.route("/api/get_formats", methods=["GET"])
def get_formats():
    """
    Получить перечень поддерживаемых форматов отчетов (текстовый вид)
    """
    formats = [item.name for item in report_type_enum]
    return ",".join(formats), 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/api/get_report", methods=["GET"])
def get_report():
    """
    Базовый проверочный эндпоинт
    """
    return "success"


@app.route("/api/get_entities", methods=["GET"])
def get_entities():
    """
    Получить перечень зарегистрированных доменных категорий хранилища
    """
    domain_keys = list(storage_manager.domains().keys())
    return ",".join(domain_keys), 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/api/get_default_report", methods=["GET"])
def get_default_report():
    """
    Получить отчет в формате по умолчанию по query-параметрам entity и unique_code
    """
    entity_type = request.args.get("entity", "").strip()
    identifier = request.args.get("unique_code", "").strip() or request.args.get("id", "").strip()

    if not entity_type or not identifier:
        return jsonify({"error": "Необходимо указать параметры entity и unique_code"}), 400

    entity = storage.get_by_type_and_id(entity_type, identifier)
    if not entity:
        return jsonify({"error": f"Сущность типа '{entity_type}' с идентификатором '{identifier}' не найдена"}), 404

    report = factory.create_default(entity_type)
    result_dto = report.build(entity)
    return report.create_response(result_dto, f"{entity_type}_{identifier}_default")


@app.route("/api/report/<entity_type>/<entity_id>", methods=["GET"])
def get_entity_report(entity_type: str, entity_id: str):
    """
    Формирование отчета по указанному формату, типу сущности и ее идентификатору
    """
    entity = storage.get_by_type_and_id(entity_type, entity_id)
    if not entity:
        return jsonify({"error": f"Сущность типа '{entity_type}' с идентификатором '{entity_id}' не найдена"}), 404

    format_arg = request.args.get("format", "").strip()
    try:
        format_enum = report_type_enum.from_string(format_arg) if format_arg else settings.settings.response_format
    except Exception as ex:
        return jsonify({"error": f"Некорректный формат отчета: {ex}"}), 400

    report = factory.create(format_enum, entity_type)
    result_dto = report.build(entity)
    return report.create_response(result_dto, f"{entity_type}_{entity_id}")


@app.route("/api/report/default/<entity_type>/<entity_id>", methods=["GET"])
def get_default_entity_report(entity_type: str, entity_id: str):
    """
    Формирование отчета с использованием формата по умолчанию (REST-стиль)
    """
    entity = storage.get_by_type_and_id(entity_type, entity_id)
    if not entity:
        return jsonify({"error": f"Сущность типа '{entity_type}' с идентификатором '{entity_id}' не найдена"}), 404

    report = factory.create_default(entity_type)
    result_dto = report.build(entity)
    return report.create_response(result_dto, f"{entity_type}_{entity_id}_default")


# -----------------------------------------------------------------------------
# CRUD-эндпоинты для управления доменными сущностями
# -----------------------------------------------------------------------------


@app.route("/api/entities/<entity_type>", methods=["GET"])
def get_entities_list(entity_type: str):
    """
    Получить список всех сущностей указанной категории в формате JSON
    """
    category = storage.resolve_category(entity_type)
    if not category:
        return jsonify({"error": f"Категория '{entity_type}' не найдена"}), 404

    items = storage.get_all(category)
    serialized = [conv.factory.domain_convertor.convert(item) for item in items]
    return jsonify(serialized), 200


@app.route("/api/entities/<entity_type>/<entity_id>", methods=["GET"])
def get_entity_by_id(entity_type: str, entity_id: str):
    """
    Получить сущность по идентификатору в формате JSON
    """
    entity = storage.get_by_type_and_id(entity_type, entity_id)
    if not entity:
        return jsonify({"error": f"Сущность типа '{entity_type}' с идентификатором '{entity_id}' не найдена"}), 404

    serialized = conv.factory.domain_convertor.convert(entity)
    return jsonify(serialized), 200


@app.route("/api/entities/<entity_type>", methods=["POST"])
def post_entity(entity_type: str):
    """
    Добавить новую сущность в хранилище
    """
    category = storage.resolve_category(entity_type)
    if not category:
        return jsonify({"error": f"Категория '{entity_type}' не найдена"}), 404

    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Требуется JSON-объект в теле запроса"}), 400

    model_cls = storage.get_model_type(category)
    try:
        context = {}
        for cat in storage.keys():
            for item in storage.get_all(cat):
                context[item.id] = item

        model_instance = conv.deserialize(data, target_type=model_cls, context=context)
        if not isinstance(model_instance, model_cls):
            return jsonify({"error": f"Не удалось преобразовать входные данные в модель {model_cls.__name__}"}), 400

        storage.add(category, model_instance)
        serialized = conv.factory.domain_convertor.convert(model_instance)
        return jsonify(serialized), 201
    except Exception as ex:
        return jsonify({"error": f"Ошибка добавления сущности: {ex}"}), 400


@app.route("/api/entities/<entity_type>/<entity_id>", methods=["PUT"])
def put_entity(entity_type: str, entity_id: str):
    """
    Обновить сущность в хранилище с контролем целостности
    """
    category = storage.resolve_category(entity_type)
    if not category:
        return jsonify({"error": f"Категория '{entity_type}' не найдена"}), 404

    existing = storage.get_by_type_and_id(category, entity_id)
    if not existing:
        return jsonify({"error": f"Сущность типа '{entity_type}' с идентификатором '{entity_id}' не найдена"}), 404

    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Требуется JSON-объект в теле запроса"}), 400

    model_cls = storage.get_model_type(category)
    try:
        context = {}
        for cat in storage.keys():
            for item in storage.get_all(cat):
                context[item.id] = item

        updated_instance = conv.deserialize(data, target_type=model_cls, context=context)
        storage.update(category, entity_id, updated_instance)
        serialized = conv.factory.domain_convertor.convert(updated_instance)
        return jsonify(serialized), 200
    except operation_exception as ex:
        if "Запрещено изменять код" in str(ex):
            return jsonify({"error": str(ex)}), 409
        return jsonify({"error": str(ex)}), 400
    except Exception as ex:
        return jsonify({"error": f"Ошибка обновления сущности: {ex}"}), 400


@app.route("/api/entities/<entity_type>/<entity_id>", methods=["DELETE"])
def delete_entity(entity_type: str, entity_id: str):
    """
    Удалить сущность из хранилища с контролем ссылочной целостности
    """
    category = storage.resolve_category(entity_type)
    if not category:
        return jsonify({"error": f"Категория '{entity_type}' не найдена"}), 404

    existing = storage.get_by_type_and_id(category, entity_id)
    if not existing:
        return jsonify({"error": f"Сущность типа '{entity_type}' с идентификатором '{entity_id}' не найдена"}), 404

    allowed, reason = storage.can_delete(category, entity_id)
    if not allowed:
        return jsonify({"error": f"Запрещено удалять сущность: {reason}"}), 409

    storage.delete(category, entity_id)
    return jsonify({"success": True, "message": f"Сущность '{entity_id}' успешно удалена"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
