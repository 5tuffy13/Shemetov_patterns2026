from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_report_factory import abstract_report_factory
from Src.Core.exception import argument_exception
from Src.Core.validator import validator
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.text_report import text_report


class report_factory(abstract_report_factory):
    """
    Реализация фабрики для построения отчетов
    """

    def __init__(self):
        """
        Инициализация фабрики и регистрация соответствий типов отчетов
        """
        self.__mapping: dict[report_type_enum, type[abstract_report]] = {
            report_type_enum.TXT: text_report
        }

    def create(self, report_type: report_type_enum) -> abstract_report:
        """
        Создать экземпляр отчета заданного типа
        """
        validator.validate_type(report_type, report_type_enum, field_name="report_type")

        if report_type not in self.__mapping:
            raise argument_exception("report_type", f"Указанный тип отчета {report_type} не реализован!")

        report_class = self.__mapping[report_type]
        return report_class()
