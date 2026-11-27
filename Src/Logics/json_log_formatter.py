import json
from typing import List
from Src.Core.abstract_log_formatter import abstract_log_formatter
from Src.Core.validator import validator
from Src.Dtos.log_entry_dto import log_entry_dto
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.log_entry_model import log_entry_model


class json_log_formatter(abstract_log_formatter):
    """
    Форматтер выгрузки записей журнала событий в JSON
    """

    @property
    def mimetype(self) -> str:
        return "application/json; charset=utf-8"

    @property
    def is_attachment(self) -> bool:
        return False

    @property
    def file_extension(self) -> str:
        return "json"

    def build(self, entries: List[log_entry_model]) -> report_result_dto:
        """
        Сформировать JSON-представление списка записей журнала
        """
        validator.validate_type(entries, list, field_name="entries")
        payload = []
        for entry in entries:
            validator.validate_type(entry, log_entry_model, field_name="entry")
            payload.append(log_entry_dto().from_domain_model(entry).to_dict())

        result = report_result_dto()
        result.text = json.dumps(payload, ensure_ascii=False, indent=2)
        result.format = self.mimetype
        return result
