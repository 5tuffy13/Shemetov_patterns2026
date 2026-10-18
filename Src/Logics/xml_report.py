import xml.etree.ElementTree as ET
from Src.Core.abstract_reference import abstract_reference
from Src.Core.abstract_report import abstract_report
from Src.Core.exception import argument_exception
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model


class xml_report(abstract_report):
    """
    Базовый построитель отчетов в формате XML
    """

    _handlers = {}

    @property
    def mimetype(self) -> str:
        return "application/xml; charset=utf-8"

    @property
    def is_attachment(self) -> bool:
        return False

    @property
    def file_extension(self) -> str:
        return "xml"

    def build(self, source: abstract_reference) -> report_result_dto:
        validator.validate_type(source, abstract_reference, field_name="source")
        reporter_cls = self._handlers.get(type(source))
        if not reporter_cls:
            raise argument_exception("source", f"Формирование XML-отчета для типа '{type(source).__name__}' не поддерживается!")
        return reporter_cls().build(source)


class receipt_xml_report(xml_report):
    """
    Построитель XML-отчета по технологической карте
    """

    def build(self, source: receipt_model) -> report_result_dto:
        validator.validate_type(source, receipt_model, field_name="source")
        root = ET.Element("receipt", attrib={"id": str(source.id), "name": source.name})
        ET.SubElement(root, "portions").text = str(source.portions)
        ET.SubElement(root, "cooking_time").text = str(source.cooking_time)
        ET.SubElement(root, "gross_total").text = str(source.gross)
        ET.SubElement(root, "net_total").text = str(source.net)

        rows_el = ET.SubElement(root, "items")
        for row in source.rows:
            row_el = ET.SubElement(rows_el, "item", attrib={"id": str(row.id)})
            ET.SubElement(row_el, "name").text = str(row.name)
            ET.SubElement(row_el, "gross").text = str(row.gross)
            ET.SubElement(row_el, "net").text = str(row.net)

        result = report_result_dto()
        result.text = ET.tostring(root, encoding="utf-8").decode("utf-8")
        return result


class nomenclature_xml_report(xml_report):
    """
    Построитель XML-отчета по номенклатуре
    """

    def build(self, source: nomenclature_model) -> report_result_dto:
        validator.validate_type(source, nomenclature_model, field_name="source")
        root = ET.Element("nomenclature", attrib={"id": str(source.id), "name": source.name})
        ET.SubElement(root, "full_name").text = str(source.full_name)
        ET.SubElement(root, "group").text = source.group.name if source.group else ""
        ET.SubElement(root, "range").text = source.range.name if source.range else ""

        result = report_result_dto()
        result.text = ET.tostring(root, encoding="utf-8").decode("utf-8")
        return result


class range_xml_report(xml_report):
    """
    Построитель XML-отчета по единице измерения
    """

    def build(self, source: range_model) -> report_result_dto:
        validator.validate_type(source, range_model, field_name="source")
        root = ET.Element("range", attrib={"id": str(source.id), "name": source.name})
        ET.SubElement(root, "coeff").text = str(source.coeff)
        ET.SubElement(root, "base_range").text = source.base_range.name if source.base_range else ""

        result = report_result_dto()
        result.text = ET.tostring(root, encoding="utf-8").decode("utf-8")
        return result


xml_report._handlers = {
    receipt_model: receipt_xml_report,
    nomenclature_model: nomenclature_xml_report,
    range_model: range_xml_report,
}
