from typing import List
from Src.Core.abstract_log_formatter import abstract_log_formatter
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.log_entry_model import log_entry_model


class markdown_log_formatter(abstract_log_formatter):
    """
    Форматтер выгрузки записей журнала в Markdown для просмотра в браузере
    """

    @property
    def mimetype(self) -> str:
        return "text/markdown; charset=utf-8"

    @property
    def is_attachment(self) -> bool:
        return False

    @property
    def file_extension(self) -> str:
        return "md"

    def build(self, entries: List[log_entry_model]) -> report_result_dto:
        """
        Сформировать Markdown-таблицу журнала событий
        """
        validator.validate_type(entries, list, field_name="entries")
        lines = [
            "# Журнал событий",
            "",
            "| Период | Подсистема | Уровень | Сообщение |",
            "| :--- | :--- | :---: | :--- |",
        ]

        for entry in entries:
            validator.validate_type(entry, log_entry_model, field_name="entry")
            safe_subsystem = entry.subsystem.replace("|", "\\|")
            safe_message = (
                entry.message.replace("|", "\\|")
                .replace("\r", " ")
                .replace("\n", " ")
            )
            lines.append(
                f"| {entry.period.isoformat()} | {safe_subsystem} | {entry.level.value} | {safe_message} |"
            )

        result = report_result_dto()
        result.text = "\n".join(lines)
        result.format = self.mimetype
        return result
