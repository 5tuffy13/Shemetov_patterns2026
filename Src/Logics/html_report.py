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
    Реализация отчета в формате HTML со структурированным текстовым представлением
    """

    def build(self, source: abstract_reference) -> report_result_dto:
        """
        Формирование отчета в формате HTML
        """
        validator.validate_type(source, abstract_reference, field_name="source")

        if isinstance(source, receipt_model):
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
        elif isinstance(source, nomenclature_model):
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
        elif isinstance(source, range_model):
            base_name = source.base_range.name if source.base_range else "—"
            html_text = (
                f"<div class=\"report-range\">"
                f"<h1>{html.escape(source.name)}</h1>"
                f"<p>Код: {html.escape(source.id)}</p>"
                f"<p>Коэффициент: {source.coeff}</p>"
                f"<p>Базовая единица: {html.escape(base_name)}</p>"
                f"</div>"
            )
        else:
            raise argument_exception("source", f"Формирование HTML-отчета для типа '{type(source).__name__}' не поддерживается!")

        result = report_result_dto()
        result.text = html_text
        return result
