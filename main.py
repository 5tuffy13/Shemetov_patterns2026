import sys
from pathlib import Path
from flask import Flask, jsonify, request

repo_root = Path(__file__).resolve().parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.report_factory import report_factory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager

app = Flask(__name__)

# Инициализация синглтонов хранилища и настроек
settings = settings_manager()
try:
    settings.load()
except Exception:
    pass

storage = storage_manager()
storage.first_start()
factory = report_factory(settings)


@app.route("/api/get_report", methods=["GET"])
def get_report():
    """
    Базовый проверочный эндпоинт
    """
    return "success"


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
    Формирование отчета с использованием формата по умолчанию (create_default)
    """
    entity = storage.get_by_type_and_id(entity_type, entity_id)
    if not entity:
        return jsonify({"error": f"Сущность типа '{entity_type}' с идентификатором '{entity_id}' не найдена"}), 404

    report = factory.create_default(entity_type)
    result_dto = report.build(entity)
    return report.create_response(result_dto, f"{entity_type}_{entity_id}_default")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
