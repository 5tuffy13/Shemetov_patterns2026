from typing import Optional
from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_report_factory import abstract_report_factory
from Src.Core.exception import argument_exception
from Src.Core.validator import validator
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.csv_report import csv_report
from Src.Logics.html_report import html_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.settings_manager import settings_manager
from Src.Logics.text_report import text_report
from Src.Logics.xml_report import xml_report


class report_factory(abstract_report_factory):
    """
    Реализация фабрики для построения отчетов
    """

    def __init__(self, manager: Optional[settings_manager] = None):
        """
        Инициализация фабрики и инкапсуляция настроек
        """
        self.__settings_manager = manager if manager is not None else settings_manager()
        self.__mapping: dict[report_type_enum, type[abstract_report]] = {
            report_type_enum.TXT: text_report,
            report_type_enum.CSV: csv_report,
            report_type_enum.MARKDOWN: markdown_report,
            report_type_enum.XML: xml_report,
            report_type_enum.HTML: html_report,
        }

    @property
    def manager(self) -> settings_manager:
        """
        Менеджер настроек
        """
        return self.__settings_manager

    def create(self, report_type: report_type_enum) -> abstract_report:
        """
        Создать экземпляр отчета заданного типа
        """
        validator.validate_type(report_type, report_type_enum, field_name="report_type")

        if report_type not in self.__mapping:
            raise argument_exception("report_type", f"Указанный тип отчета {report_type} не реализован!")

        report_class = self.__mapping[report_type]
        return report_class()

    def create_default(self) -> abstract_report:
        """
        Создать экземпляр отчета формата, установленного в настройках по умолчанию
        """
        default_format = self.__settings_manager.settings.response_format
        return self.create(default_format)
