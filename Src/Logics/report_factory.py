from typing import Optional
from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_report_factory import abstract_report_factory
from Src.Core.exception import argument_exception
from Src.Core.validator import validator
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.csv_report import (
    csv_report,
    nomenclature_csv_report,
    range_csv_report,
    receipt_csv_report,
)
from Src.Logics.html_report import (
    html_report,
    nomenclature_html_report,
    range_html_report,
    receipt_html_report,
)
from Src.Logics.markdown_report import (
    markdown_report,
    nomenclature_markdown_report,
    range_markdown_report,
    receipt_markdown_report,
)
from Src.Logics.settings_manager import settings_manager
from Src.Logics.text_report import (
    nomenclature_text_report,
    range_text_report,
    receipt_text_report,
    text_report,
)
from Src.Logics.xml_report import (
    nomenclature_xml_report,
    range_xml_report,
    receipt_xml_report,
    xml_report,
)


class report_factory(abstract_report_factory):
    """
    Реализация фабрики для построения отчетов
    """

    def __init__(self, manager: Optional[settings_manager] = None):
        """
        Инициализация фабрики и инкапсуляция настроек
        """
        self.__settings_manager = manager if manager is not None else settings_manager()

        # Реестр специализированных генераторов по парам (формат, сущность)
        self.__mapping: dict[tuple[report_type_enum, str], type[abstract_report]] = {
            (report_type_enum.TXT, "receipt"): receipt_text_report,
            (report_type_enum.TXT, "nomenclature"): nomenclature_text_report,
            (report_type_enum.TXT, "range"): range_text_report,

            (report_type_enum.CSV, "receipt"): receipt_csv_report,
            (report_type_enum.CSV, "nomenclature"): nomenclature_csv_report,
            (report_type_enum.CSV, "range"): range_csv_report,

            (report_type_enum.MARKDOWN, "receipt"): receipt_markdown_report,
            (report_type_enum.MARKDOWN, "nomenclature"): nomenclature_markdown_report,
            (report_type_enum.MARKDOWN, "range"): range_markdown_report,

            (report_type_enum.XML, "receipt"): receipt_xml_report,
            (report_type_enum.XML, "nomenclature"): nomenclature_xml_report,
            (report_type_enum.XML, "range"): range_xml_report,

            (report_type_enum.HTML, "receipt"): receipt_html_report,
            (report_type_enum.HTML, "nomenclature"): nomenclature_html_report,
            (report_type_enum.HTML, "range"): range_html_report,
        }

        # Реестр базовых генераторов по формату
        self.__format_mapping: dict[report_type_enum, type[abstract_report]] = {
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

    @staticmethod
    def normalize_entity_type(entity_type: str) -> str:
        """
        Нормализация наименования типа сущности
        """
        if not isinstance(entity_type, str):
            return ""
        norm = entity_type.strip().lower()
        aliases = {
            "receipt_model": "receipt",
            "рецепт": "receipt",
            "nomenclature_model": "nomenclature",
            "номенклатура": "nomenclature",
            "range_model": "range",
            "единица_измерения": "range",
            "единица": "range",
        }
        return aliases.get(norm, norm)

    def create(self, report_type: report_type_enum, entity_type: str = "") -> abstract_report:
        """
        Создать экземпляр отчета заданного типа и сущности
        """
        validator.validate_type(report_type, report_type_enum, field_name="report_type")

        if entity_type:
            norm_entity = self.normalize_entity_type(entity_type)
            key = (report_type, norm_entity)
            if key in self.__mapping:
                return self.__mapping[key]()

        if report_type not in self.__format_mapping:
            raise argument_exception("report_type", f"Указанный тип отчета {report_type} не реализован!")

        return self.__format_mapping[report_type]()

    def create_default(self, entity_type: str = "") -> abstract_report:
        """
        Создать экземпляр отчета формата, установленного в настройках по умолчанию
        """
        default_format = self.__settings_manager.settings.response_format
        return self.create(default_format, entity_type)
