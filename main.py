import io
import sys
from pathlib import Path
from flask import Flask, Response, abort, jsonify, request

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


def _find_entity(entity_type: str, entity_id: str):
    """
    Поиск сущности в хранилище данных по типу и идентификатору/имени
    """
    normalized_type = entity_type.strip().lower()

    if normalized_type in ["receipt", "рецепт", "receipt_model"]:
        receipt = storage.get_receipt(entity_id)
        if receipt:
            return receipt
        for r in storage.receipts:
            if r.id == entity_id or r.name.lower() == entity_id.lower():
                return r

    elif normalized_type in ["nomenclature", "номенклатура", "nomenclature_model"]:
        for n in storage.nomenclatures:
            if n.id == entity_id or n.name.lower() == entity_id.lower():
                return n

    elif normalized_type in ["range", "единица_измерения", "единица", "range_model"]:
        for r in storage.ranges:
            if r.id == entity_id or r.name.lower() == entity_id.lower():
                return r

    return None


def _build_response(report, entity, format_enum: report_type_enum, filename_prefix: str) -> Response:
    """
    Формирование HTTP-ответа в соответствии с требованиями ТЗ:
    бинарная выгрузка файла для Markdown и CSV, структурированный текст для остальных.
    """
    result_dto = report.build(entity)

    if format_enum == report_type_enum.MARKDOWN:
        return Response(
            bytes(result_dto.binary),
            mimetype="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename_prefix}.md"'},
        )
    elif format_enum == report_type_enum.CSV:
        return Response(
            bytes(result_dto.binary),
            mimetype="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename_prefix}.csv"'},
        )
    elif format_enum == report_type_enum.XML:
        return Response(result_dto.text, mimetype="application/xml; charset=utf-8")
    elif format_enum == report_type_enum.HTML:
        return Response(result_dto.text, mimetype="text/html; charset=utf-8")
    else:
        return Response(result_dto.text, mimetype="text/plain; charset=utf-8")


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
    entity = _find_entity(entity_type, entity_id)
    if not entity:
        return jsonify({"error": f"Сущность типа '{entity_type}' с идентификатором '{entity_id}' не найдена"}), 404

    format_arg = request.args.get("format", "").strip()
    try:
        format_enum = report_type_enum.from_string(format_arg) if format_arg else settings.settings.response_format
    except Exception as ex:
        return jsonify({"error": f"Некорректный формат отчета: {ex}"}), 400

    report = factory.create(format_enum)
    return _build_response(report, entity, format_enum, f"{entity_type}_{entity_id}")


@app.route("/api/report/default/<entity_type>/<entity_id>", methods=["GET"])
def get_default_entity_report(entity_type: str, entity_id: str):
    """
    Формирование отчета с использованием формата по умолчанию (create_default)
    """
    entity = _find_entity(entity_type, entity_id)
    if not entity:
        return jsonify({"error": f"Сущность типа '{entity_type}' с идентификатором '{entity_id}' не найдена"}), 404

    default_format = settings.settings.response_format
    report = factory.create_default()
    return _build_response(report, entity, default_format, f"{entity_type}_{entity_id}_default")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
