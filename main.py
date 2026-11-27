import sys
import time
from pathlib import Path
from flask import Flask, g, jsonify, request

repo_root = Path(__file__).resolve().parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Core.event_type_enum import event_type_enum
from Src.Core.exception import operation_exception
from Src.Core.log_level_enum import log_level_enum
from Src.Core.sort_direction_enum import sort_direction_enum
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_item_dto import filter_item_dto
from Src.Dtos.filter_type_enum import filter_type_enum
from Src.Dtos.log_format_enum import log_format_enum
from Src.Dtos.log_query_dto import log_query_dto
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.convertor import convertor
from Src.Logics.log_formatter_factory import log_formatter_factory
from Src.Logics.log_service import log_service
from Src.Logics.observer import observer
from Src.Logics.osv_service import osv_service
from Src.Logics.prototype import prototype
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

# Инициализация сервиса логирования, настроек, хранилища и конвертора
log_svc = log_service()
log_fmt_factory = log_formatter_factory()

settings = settings_manager()
try:
    settings.load()
except Exception:
    pass

storage = storage_manager()
storage.first_start()
factory = report_factory(settings)
conv = convertor()


@app.before_request
def log_http_request_started():
    """
    Фиксация начала обработки входящего HTTP-запроса
    """
    g.request_started_at = time.perf_counter()
    observer().notify(
        event_type_enum.HTTP_REQUEST_STARTED,
        {
            "subsystem": "web_api",
            "level": log_level_enum.DEBUG,
            "message": f"Входящий запрос {request.method} {request.path}",
        },
    )


@app.after_request
def log_http_request_completed(response):
    """
    Фиксация завершения HTTP-запроса с кодом ответа и длительностью
    """
    started_at = getattr(g, "request_started_at", None)
    elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2) if started_at is not None else 0.0
    level = log_level_enum.ERROR if response.status_code >= 400 else log_level_enum.INFO
    observer().notify(
        event_type_enum.HTTP_REQUEST_COMPLETED,
        {
            "subsystem": "web_api",
            "level": level,
            "message": f"{request.method} {request.path} -> {response.status_code} ({elapsed_ms} ms)",
        },
    )
    return response


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


# -----------------------------------------------------------------------------
# Эндпоинты фильтрации через Прототип и Оборотно-сальдовой ведомости (ОСВ)
# -----------------------------------------------------------------------------


@app.route("/api/filter/<domain>", methods=["POST"])
def post_filter_domain(domain: str):
    """
    Фильтрация доменных сущностей с использованием паттерна Прототип
    """
    category = storage.resolve_category(domain)
    if not category:
        return jsonify({"error": f"Категория '{domain}' не найдена"}), 404

    data = request.get_json(silent=True) or {}
    try:
        filter_obj = filter_dto.from_dict(data)
    except Exception as ex:
        return jsonify({"error": f"Некорректный формат фильтра: {ex}"}), 400

    items = storage.get_all(category)
    pr = prototype(items).clone(filter_obj)
    serialized = [conv.factory.domain_convertor.convert(item) for item in pr.data]
    return jsonify(serialized), 200


@app.route("/api/osv/filter", methods=["POST"])
def post_osv_filter():
    """
    Формирование Оборотно-сальдовой ведомости (ОСВ) с фильтрацией через Прототип
    """
    data = request.get_json(silent=True) or {}
    try:
        filter_obj = filter_dto.from_dict(data) if data else None
    except Exception as ex:
        return jsonify({"error": f"Некорректный формат фильтра: {ex}"}), 400

    osv_svc = osv_service(storage)
    rows = osv_svc.build(filter_obj)
    return jsonify([row.to_dict() for row in rows]), 200


# -----------------------------------------------------------------------------
# Эндпоинты журнала событий (Логирование)
# -----------------------------------------------------------------------------


def _build_log_query_from_args() -> log_query_dto:
    """
    Сборка параметров запроса журнала из query-параметров HTTP-запроса
    """
    filter_obj = filter_dto()

    level_arg = request.args.get("level")
    if level_arg is not None and level_arg.strip():
        lvl = log_level_enum.from_string(level_arg)
        filter_obj.add_item(filter_item_dto("level", filter_type_enum.EQUALS, lvl.value))

    subsystem_arg = request.args.get("subsystem")
    if subsystem_arg is not None and subsystem_arg.strip():
        filter_obj.add_item(filter_item_dto("subsystem", filter_type_enum.LIKE, subsystem_arg.strip()))

    sort_by_arg = request.args.get("sort_by", "period")
    if not sort_by_arg.strip():
        sort_by_arg = "period"

    sort_dir_arg = request.args.get("sort_direction", "DESC")
    sort_dir = sort_direction_enum.from_string(sort_dir_arg)

    return log_query_dto(
        filter_obj=filter_obj if len(filter_obj) > 0 else None,
        sort_by=sort_by_arg,
        sort_direction=sort_dir,
    )


@app.route("/api/logs", methods=["GET"])
def get_logs():
    """
    Получить записи журнала событий в формате JSON с опциональной фильтрацией и сортировкой
    """
    try:
        query = _build_log_query_from_args()
        entries = log_svc.query(query)
        formatter = log_fmt_factory.create(log_format_enum.JSON)
        return formatter.create_response(entries, "logs")
    except Exception as ex:
        return jsonify({"error": f"Некорректные параметры запроса журнала: {ex}"}), 400


@app.route("/api/logs/filter", methods=["POST"])
def post_logs_filter():
    """
    Фильтрация и сортировка записей журнала событий через Прототип
    """
    raw_data = request.get_json(silent=True)
    if raw_data is None:
        raw_data = {}
    if not isinstance(raw_data, dict):
        return jsonify({"error": "Требуется JSON-объект в теле запроса"}), 400

    try:
        query = log_query_dto.from_dict(raw_data)
        entries = log_svc.query(query)
        formatter = log_fmt_factory.create(log_format_enum.JSON)
        return formatter.create_response(entries, "logs")
    except Exception as ex:
        return jsonify({"error": f"Некорректные параметры фильтрации журнала: {ex}"}), 400


@app.route("/api/logs/export", methods=["GET"])
def get_logs_export():
    """
    Экспорт записей журнала событий в указанном формате (TXT, CSV, MARKDOWN, JSON)
    """
    try:
        format_arg = request.args.get("format") if "format" in request.args else "TXT"
        fmt_enum = log_format_enum.from_string(format_arg)
        formatter = log_fmt_factory.create(fmt_enum)
        query = _build_log_query_from_args()
        entries = log_svc.query(query)
        return formatter.create_response(entries, "logs")
    except Exception as ex:
        return jsonify({"error": f"Ошибка экспорта журнала: {ex}"}), 400


@app.route("/api/logs/export", methods=["POST"])
def post_logs_export():
    """
    Экспорт отфильтрованных записей журнала событий в указанном формате
    """
    raw_data = request.get_json(silent=True)
    if raw_data is None:
        raw_data = {}
    if not isinstance(raw_data, dict):
        return jsonify({"error": "Требуется JSON-объект в теле запроса"}), 400

    try:
        if "format" in request.args:
            format_arg = request.args.get("format")
        elif "format" in raw_data:
            format_arg = raw_data.get("format")
        else:
            format_arg = "TXT"

        fmt_enum = log_format_enum.from_string(format_arg)
        formatter = log_fmt_factory.create(fmt_enum)
        query = log_query_dto.from_dict(raw_data) if raw_data else _build_log_query_from_args()
        entries = log_svc.query(query)
        return formatter.create_response(entries, "logs")
    except Exception as ex:
        return jsonify({"error": f"Ошибка экспорта журнала: {ex}"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
