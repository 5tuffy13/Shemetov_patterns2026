from abc import ABC, abstractmethod
from Src.Core.abstract_reference import abstract_reference
from Src.Dtos.report_result_dto import report_result_dto


class abstract_report(ABC):
    """
    Абстрактный класс для формирования отчета
    """

    @abstractmethod
    def build(self, source: abstract_reference) -> report_result_dto:
        """
        Сформировать отчет по переданному источнику данных
        """
        pass
