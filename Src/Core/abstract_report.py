from abc import ABC, abstractmethod
from Src.Core.abstract_reference import abstract_reference
from Src.Dtos.report_result_dto import report_result_dto


class abstract_report(ABC):
    """
    Абстрактный базовый класс для формирования отчета
    """

    @property
    @abstractmethod
    def mimetype(self) -> str:
        """
        MIME-тип представления отчета
        """
        pass

    @property
    def is_attachment(self) -> bool:
        """
        Признак передачи отчета в виде скачиваемого вложения
        """
        return False

    @property
    def file_extension(self) -> str:
        """
        Расширение файла отчета
        """
        return "txt"

    def create_response(self, result: report_result_dto, filename_prefix: str = "report"):
        """
        Полиморфное построение HTTP-ответа без процедурных ветвлений
        """
        from flask import Response

        data = bytes(result.binary) if self.is_attachment else result.text
        headers = {}
        if self.is_attachment:
            headers["Content-Disposition"] = f'attachment; filename="{filename_prefix}.{self.file_extension}"'
        return Response(data, mimetype=self.mimetype, headers=headers)

    @abstractmethod
    def build(self, source: abstract_reference) -> report_result_dto:
        """
        Сформировать отчет по переданному источнику данных
        """
        pass
