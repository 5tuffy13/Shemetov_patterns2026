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
    Реализация отчета в формате XML со структурированным текстовым представлением
    """

    def build(self, source: abstract_reference) -> report_result_dto:
        """
        Формирование отчета в формате XML
        """
        validator.validate_type(source, abstract_reference, field_name="source")

        if isinstance(source, receipt_model):
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

            xml_text = ET.tostring(root, encoding="utf-8").decode("utf-8")
        elif isinstance(source, nomenclature_model):
            root = ET.Element("nomenclature", attrib={"id": str(source.id), "name": source.name})
            ET.SubElement(root, "full_name").text = str(source.full_name)
            ET.SubElement(root, "group").text = source.group.name if source.group else ""
            ET.SubElement(root, "range").text = source.range.name if source.range else ""
            xml_text = ET.tostring(root, encoding="utf-8").decode("utf-8")
        elif isinstance(source, range_model):
            root = ET.Element("range", attrib={"id": str(source.id), "name": source.name})
            ET.SubElement(root, "coeff").text = str(source.coeff)
            ET.SubElement(root, "base_range").text = source.base_range.name if source.base_range else ""
            xml_text = ET.tostring(root, encoding="utf-8").decode("utf-8")
        else:
            raise argument_exception("source", f"Формирование XML-отчета для типа '{type(source).__name__}' не поддерживается!")

        result = report_result_dto()
        result.text = xml_text
        return result
