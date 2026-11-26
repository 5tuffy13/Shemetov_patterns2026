import csv
import io
from typing import List
from Src.Core.abstract_log_formatter import abstract_log_formatter
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.log_entry_model import log_entry_model


class csv_log_formatter(abstract_log_formatter):
    """
    Форматтер выгрузки записей журнала в CSV с разделителем ';' и UTF-8 BOM для Excel
    """

    @property
    def mimetype(self) -> str:
        return "text/csv; charset=utf-8"

    @property
    def is_attachment(self) -> bool:
        return True

    @property
    def file_extension(self) -> str:
        return "csv"

    def build(self, entries: List[log_entry_model]) -> report_result_dto:
        """
        Сформировать CSV-таблицу журнала событий
        """
        validator.validate_type(entries, list, field_name="entries")
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter=";", lineterminator="\n")
        writer.writerow(["Период", "Подсистема", "Уровень", "Тип события", "Сообщение"])

        for entry in entries:
            validator.validate_type(entry, log_entry_model, field_name="entry")
            writer.writerow([
                entry.period.isoformat(),
                entry.subsystem,
                entry.level.value,
                entry.event_type.value,
                entry.message,
            ])

        csv_bytes = ("\ufeff" + buffer.getvalue()).encode("utf-8")
        result = report_result_dto()
        result.binary = csv_bytes
        result.format = self.mimetype
        return result
