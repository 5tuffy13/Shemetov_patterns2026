from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from Src.Dtos.report_result_dto import report_result_dto
    from Src.Models.log_entry_model import log_entry_model


class abstract_log_formatter(ABC):
    """
    Абстрактный базовый класс форматтера выгрузки журнала событий
    """

    @property
    @abstractmethod
    def mimetype(self) -> str:
        """
        MIME-тип формируемого представления журнала
        """
        pass

    @property
    @abstractmethod
    def is_attachment(self) -> bool:
        """
        Признак отдачи результата в виде скачиваемого файла-вложения
        """
        pass

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """
        Расширение файла выгрузки
        """
        pass

    @abstractmethod
    def build(self, entries: List["log_entry_model"]) -> "report_result_dto":
        """
        Сформировать представление списка записей журнала
        """
        pass

    def create_response(self, entries: List["log_entry_model"], filename_prefix: str = "logs"):
        """
        Сборка HTTP-ответа на основе метаданных конкретного форматтера
        """
        from flask import Response

        result = self.build(entries)
        if self.is_attachment:
            data = bytes(result.binary) if result.binary else result.text.encode("utf-8")
            headers = {
                "Content-Disposition": f'attachment; filename="{filename_prefix}.{self.file_extension}"'
            }
        else:
            data = result.text if result.text else bytes(result.binary).decode("utf-8")
            headers = {}

        return Response(data, mimetype=self.mimetype, headers=headers)
