from typing import List
from Src.Core.abstract_log_formatter import abstract_log_formatter
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.log_entry_model import log_entry_model


class text_log_formatter(abstract_log_formatter):
    """
    Форматтер выгрузки записей журнала в текстовый файл для блокнота (TXT)
    """

    @property
    def mimetype(self) -> str:
        return "text/plain; charset=utf-8"

    @property
    def is_attachment(self) -> bool:
        return True

    @property
    def file_extension(self) -> str:
        return "txt"

    def build(self, entries: List[log_entry_model]) -> report_result_dto:
        """
        Сформировать построчное текстовое представление журнала
        """
        validator.validate_type(entries, list, field_name="entries")
        lines = []
        for entry in entries:
            validator.validate_type(entry, log_entry_model, field_name="entry")
            lines.append(
                f"{entry.period.isoformat()} | {entry.subsystem} | {entry.level.value} | {entry.message}"
            )

        content = "\n".join(lines)
        result = report_result_dto()
        result.binary = content.encode("utf-8")
        result.format = self.mimetype
        return result
