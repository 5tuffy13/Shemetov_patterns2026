from Src.Core.abstract_reference import abstract_reference
from Src.Core.abstract_report import abstract_report
from Src.Core.exception import argument_exception
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model


class text_report(abstract_report):
    """
    Базовый построитель отчетов в текстовом формате (TXT)
    """

    _handlers = {}

    @property
    def mimetype(self) -> str:
        return "text/plain; charset=utf-8"

    @property
    def is_attachment(self) -> bool:
        return False

    @property
    def file_extension(self) -> str:
        return "txt"

    def build(self, source: abstract_reference) -> report_result_dto:
        validator.validate_type(source, abstract_reference, field_name="source")
        reporter_cls = self._handlers.get(type(source))
        if not reporter_cls:
            raise argument_exception("source", f"Формирование текстового отчета для типа '{type(source).__name__}' не поддерживается!")
        return reporter_cls().build(source)


class receipt_text_report(text_report):
    """
    Построитель текстового отчета по технологической карте
    """

    def build(self, source: receipt_model) -> report_result_dto:
        validator.validate_type(source, receipt_model, field_name="source")
        header = "Код | Наименование | Брутто | Нетто "
        data = ""
        for row in source.rows:
            code = row.id
            name = row.name
            gross = row.gross
            net = row.net
            data += f"\n{code} | {name} | {gross} | {net}"

        result = report_result_dto()
        result.text = f"{header}{data}"
        return result


class nomenclature_text_report(text_report):
    """
    Построитель текстового отчета по номенклатуре
    """

    def build(self, source: nomenclature_model) -> report_result_dto:
        validator.validate_type(source, nomenclature_model, field_name="source")
        range_name = source.range.name if source.range else ""
        group_name = source.group.name if source.group else ""
        text = (
            f"Номенклатура: {source.name}\n"
            f"Код: {source.id}\n"
            f"Полное наименование: {source.full_name}\n"
            f"Группа: {group_name}\n"
            f"Единица измерения: {range_name}"
        )

        result = report_result_dto()
        result.text = text
        return result


class range_text_report(text_report):
    """
    Построитель текстового отчета по единице измерения
    """

    def build(self, source: range_model) -> report_result_dto:
        validator.validate_type(source, range_model, field_name="source")
        base_name = source.base_range.name if source.base_range else "—"
        text = (
            f"Единица измерения: {source.name}\n"
            f"Код: {source.id}\n"
            f"Коэффициент: {source.coeff}\n"
            f"Базовая единица: {base_name}"
        )

        result = report_result_dto()
        result.text = text
        return result


text_report._handlers = {
    receipt_model: receipt_text_report,
    nomenclature_model: nomenclature_text_report,
    range_model: range_text_report,
}
