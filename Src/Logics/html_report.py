import html
from Src.Core.abstract_reference import abstract_reference
from Src.Core.abstract_report import abstract_report
from Src.Core.exception import argument_exception
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model


class html_report(abstract_report):
    """
    Базовый построитель отчетов в формате HTML
    """

    _handlers = {}

    @property
    def mimetype(self) -> str:
        return "text/html; charset=utf-8"

    @property
    def is_attachment(self) -> bool:
        return False

    @property
    def file_extension(self) -> str:
        return "html"

    def build(self, source: abstract_reference) -> report_result_dto:
        validator.validate_type(source, abstract_reference, field_name="source")
        reporter_cls = self._handlers.get(type(source))
        if not reporter_cls:
            raise argument_exception("source", f"Формирование HTML-отчета для типа '{type(source).__name__}' не поддерживается!")
        return reporter_cls().build(source)


class receipt_html_report(html_report):
    """
    Построитель HTML-отчета по технологической карте
    """

    def build(self, source: receipt_model) -> report_result_dto:
        validator.validate_type(source, receipt_model, field_name="source")
        rows_html = "".join(
            f"<tr><td>{html.escape(r.id)}</td><td>{html.escape(r.name)}</td><td>{r.gross}</td><td>{r.net}</td></tr>"
            for r in source.rows
        )
        html_text = (
            f"<div class=\"report-receipt\">"
            f"<h1>{html.escape(source.name)}</h1>"
            f"<p>Порции: {source.portions}, Время: {source.cooking_time} мин.</p>"
            f"<p>Итого Брутто: {source.gross} г, Итого Нетто: {source.net} г</p>"
            f"<table><thead><tr><th>Код</th><th>Наименование</th><th>Брутто</th><th>Нетто</th></tr></thead>"
            f"<tbody>{rows_html}</tbody></table>"
            f"</div>"
        )
        result = report_result_dto()
        result.text = html_text
        return result


class nomenclature_html_report(html_report):
    """
    Построитель HTML-отчета по номенклатуре
    """

    def build(self, source: nomenclature_model) -> report_result_dto:
        validator.validate_type(source, nomenclature_model, field_name="source")
        group_name = source.group.name if source.group else ""
        range_name = source.range.name if source.range else ""
        html_text = (
            f"<div class=\"report-nomenclature\">"
            f"<h1>{html.escape(source.name)}</h1>"
            f"<p>Код: {html.escape(source.id)}</p>"
            f"<p>Полное наименование: {html.escape(source.full_name)}</p>"
            f"<p>Группа: {html.escape(group_name)}</p>"
            f"<p>Единица измерения: {html.escape(range_name)}</p>"
            f"</div>"
        )
        result = report_result_dto()
        result.text = html_text
        return result


class range_html_report(html_report):
    """
    Построитель HTML-отчета по единице измерения
    """

    def build(self, source: range_model) -> report_result_dto:
        validator.validate_type(source, range_model, field_name="source")
        base_name = source.base_range.name if source.base_range else "—"
        html_text = (
            f"<div class=\"report-range\">"
            f"<h1>{html.escape(source.name)}</h1>"
            f"<p>Код: {html.escape(source.id)}</p>"
            f"<p>Коэффициент: {source.coeff}</p>"
            f"<p>Базовая единица: {html.escape(base_name)}</p>"
            f"</div>"
        )
        result = report_result_dto()
        result.text = html_text
        return result


html_report._handlers = {
    receipt_model: receipt_html_report,
    nomenclature_model: nomenclature_html_report,
    range_model: range_html_report,
}
