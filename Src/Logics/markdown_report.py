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
    Реализация отчета в формате Markdown с бинарным представлением результата
    """

    def build(self, source: abstract_reference) -> report_result_dto:
        """
        Формирование отчета в формате Markdown
        """
        validator.validate_type(source, abstract_reference, field_name="source")

        if isinstance(source, receipt_model):
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
            md_text = "\n".join(md_lines)
        elif isinstance(source, nomenclature_model):
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
            md_text = "\n".join(md_lines)
        elif isinstance(source, range_model):
            base_name = source.base_range.name if source.base_range else "—"
            md_lines = [
                f"# Единица измерения: {source.name}",
                "",
                f"- **Код:** `{source.id}`",
                f"- **Коэффициент пересчета:** {source.coeff}",
                f"- **Базовая единица:** {base_name}",
            ]
            md_text = "\n".join(md_lines)
        else:
            raise argument_exception("source", f"Формирование Markdown-отчета для типа '{type(source).__name__}' не поддерживается!")

        result = report_result_dto()
        result.binary = md_text.encode("utf-8")
        return result
