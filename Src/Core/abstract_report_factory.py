from abc import ABC, abstractmethod
from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_type_enum import report_type_enum


class abstract_report_factory(ABC):
    """
    Абстрактная фабрика для создания отчетов
    """

    @abstractmethod
    def create(self, report_type: report_type_enum) -> abstract_report:
        """
        Подобрать и создать экземпляр нужного отчета
        """
        pass
