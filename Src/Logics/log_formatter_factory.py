from typing import Dict, Type
from Src.Core.abstract_log_formatter import abstract_log_formatter
from Src.Core.exception import argument_exception
from Src.Core.validator import validator
from Src.Dtos.log_format_enum import log_format_enum
from Src.Logics.csv_log_formatter import csv_log_formatter
from Src.Logics.json_log_formatter import json_log_formatter
from Src.Logics.markdown_log_formatter import markdown_log_formatter
from Src.Logics.text_log_formatter import text_log_formatter


class log_formatter_factory:
    """
    Фабрика подбора форматтера выгрузки журнала событий по табличному реестру
    """

    _formatters: Dict[log_format_enum, Type[abstract_log_formatter]] = {
        log_format_enum.JSON: json_log_formatter,
        log_format_enum.TXT: text_log_formatter,
        log_format_enum.CSV: csv_log_formatter,
        log_format_enum.MARKDOWN: markdown_log_formatter,
    }

    def create(self, log_format: log_format_enum | str) -> abstract_log_formatter:
        """
        Создать экземпляр форматтера по указанному формату выгрузки
        """
        if isinstance(log_format, str):
            resolved_format = log_format_enum.from_string(log_format)
        else:
            validator.validate_type(log_format, log_format_enum, field_name="log_format")
            resolved_format = log_format

        formatter_cls = self._formatters.get(resolved_format)
        if formatter_cls is None:
            raise argument_exception("log_format", f"Форматтер для '{resolved_format}' не зарегистрирован!")

        return formatter_cls()
