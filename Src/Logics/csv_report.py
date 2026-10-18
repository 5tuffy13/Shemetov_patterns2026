from Src.Core.abstract_reference import abstract_reference
from Src.Core.abstract_report import abstract_report
from Src.Core.exception import argument_exception
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model


class csv_report(abstract_report):
    """
    Базовый построитель отчетов в формате CSV
    """

    _handlers = {}

    @property
    def mimetype(self) -> str:
        return "text/csv; charset=utf-8"

    @property
    def is_attachment(self) -> bool:
        return True

    @property
    def file_extension(self) -> str:
        return "csv"

    def build(self, source: abstract_reference) -> report_result_dto:
        validator.validate_type(source, abstract_reference, field_name="source")
        reporter_cls = self._handlers.get(type(source))
        if not reporter_cls:
            raise argument_exception("source", f"Формирование CSV-отчета для типа '{type(source).__name__}' не поддерживается!")
        return reporter_cls().build(source)


class receipt_csv_report(csv_report):
    """
    Построитель CSV-отчета по технологической карте
    """

    def build(self, source: receipt_model) -> report_result_dto:
        validator.validate_type(source, receipt_model, field_name="source")
        lines = ["id;name;gross;net"]
        for row in source.rows:
            lines.append(f"{row.id};{row.name};{row.gross};{row.net}")

        result = report_result_dto()
        result.binary = "\n".join(lines).encode("utf-8")
        return result


class nomenclature_csv_report(csv_report):
    """
    Построитель CSV-отчета по номенклатуре
    """

    def build(self, source: nomenclature_model) -> report_result_dto:
        validator.validate_type(source, nomenclature_model, field_name="source")
        range_name = source.range.name if source.range else ""
        group_name = source.group.name if source.group else ""
        lines = [
            "id;name;full_name;group;range",
            f"{source.id};{source.name};{source.full_name};{group_name};{range_name}",
        ]

        result = report_result_dto()
        result.binary = "\n".join(lines).encode("utf-8")
        return result


class range_csv_report(csv_report):
    """
    Построитель CSV-отчета по единице измерения
    """

    def build(self, source: range_model) -> report_result_dto:
        validator.validate_type(source, range_model, field_name="source")
        base_name = source.base_range.name if source.base_range else ""
        lines = [
            "id;name;coeff;base_range",
            f"{source.id};{source.name};{source.coeff};{base_name}",
        ]

        result = report_result_dto()
        result.binary = "\n".join(lines).encode("utf-8")
        return result


csv_report._handlers = {
    receipt_model: receipt_csv_report,
    nomenclature_model: nomenclature_csv_report,
    range_model: range_csv_report,
}
