from Src.Core.abstract_reference import abstract_reference
from Src.Core.abstract_report import abstract_report
from Src.Core.exception import argument_exception
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model


class markdown_report(abstract_report):
    """
    Базовый построитель отчетов в формате Markdown
    """

    _handlers = {}

    @property
    def mimetype(self) -> str:
        return "text/markdown; charset=utf-8"

    @property
    def is_attachment(self) -> bool:
        return True

    @property
    def file_extension(self) -> str:
        return "md"

    def build(self, source: abstract_reference) -> report_result_dto:
        validator.validate_type(source, abstract_reference, field_name="source")
        reporter_cls = self._handlers.get(type(source))
        if not reporter_cls:
            raise argument_exception("source", f"Формирование Markdown-отчета для типа '{type(source).__name__}' не поддерживается!")
        return reporter_cls().build(source)


class receipt_markdown_report(markdown_report):
    """
    Построитель Markdown-отчета по технологической карте
    """

    def build(self, source: receipt_model) -> report_result_dto:
        validator.validate_type(source, receipt_model, field_name="source")
        md_lines = [
            f"# Технологическая карта: {source.name}",
            "",
            f"- **Порции:** {source.portions}",
            f"- **Время приготовления:** {source.cooking_time} мин.",
            f"- **Итого Брутто:** {source.gross} г",
            f"- **Итого Нетто:** {source.net} г",
            "",
            "| Код | Наименование | Брутто (г) | Нетто (г) |",
            "| :--- | :--- | :---: | :---: |",
        ]
        for row in source.rows:
            md_lines.append(f"| `{row.id[:8]}` | {row.name} | {row.gross} | {row.net} |")

        result = report_result_dto()
        result.binary = "\n".join(md_lines).encode("utf-8")
        return result


class nomenclature_markdown_report(markdown_report):
    """
    Построитель Markdown-отчета по номенклатуре
    """

    def build(self, source: nomenclature_model) -> report_result_dto:
        validator.validate_type(source, nomenclature_model, field_name="source")
        range_name = source.range.name if source.range else "—"
        group_name = source.group.name if source.group else "—"
        md_lines = [
            f"# Номенклатура: {source.name}",
            "",
            f"- **Код:** `{source.id}`",
            f"- **Полное наименование:** {source.full_name}",
            f"- **Группа:** {group_name}",
            f"- **Единица измерения:** {range_name}",
        ]

        result = report_result_dto()
        result.binary = "\n".join(md_lines).encode("utf-8")
        return result


class range_markdown_report(markdown_report):
    """
    Построитель Markdown-отчета по единице измерения
    """

    def build(self, source: range_model) -> report_result_dto:
        validator.validate_type(source, range_model, field_name="source")
        base_name = source.base_range.name if source.base_range else "—"
        md_lines = [
            f"# Единица измерения: {source.name}",
            "",
            f"- **Код:** `{source.id}`",
            f"- **Коэффициент пересчета:** {source.coeff}",
            f"- **Базовая единица:** {base_name}",
        ]

        result = report_result_dto()
        result.binary = "\n".join(md_lines).encode("utf-8")
        return result


markdown_report._handlers = {
    receipt_model: receipt_markdown_report,
    nomenclature_model: nomenclature_markdown_report,
    range_model: range_markdown_report,
}
