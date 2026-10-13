from Src.Core.abstract_reference import abstract_reference
from Src.Core.abstract_report import abstract_report
from Src.Core.exception import argument_exception
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model


class csv_report(abstract_report):
    """
    Реализация отчета в формате CSV с бинарным представлением результата
    """

    def build(self, source: abstract_reference) -> report_result_dto:
        """
        Формирование отчета в формате CSV
        """
        validator.validate_type(source, abstract_reference, field_name="source")

        if isinstance(source, receipt_model):
            lines = ["id;name;gross;net"]
            for row in source.rows:
                lines.append(f"{row.id};{row.name};{row.gross};{row.net}")
            csv_text = "\n".join(lines)
        elif isinstance(source, nomenclature_model):
            range_name = source.range.name if source.range else ""
            group_name = source.group.name if source.group else ""
            lines = [
                "id;name;full_name;group;range",
                f"{source.id};{source.name};{source.full_name};{group_name};{range_name}",
            ]
            csv_text = "\n".join(lines)
        elif isinstance(source, range_model):
            base_name = source.base_range.name if source.base_range else ""
            lines = [
                "id;name;coeff;base_range",
                f"{source.id};{source.name};{source.coeff};{base_name}",
            ]
            csv_text = "\n".join(lines)
        else:
            raise argument_exception("source", f"Формирование CSV-отчета для типа '{type(source).__name__}' не поддерживается!")

        result = report_result_dto()
        result.binary = csv_text.encode("utf-8")
        return result
