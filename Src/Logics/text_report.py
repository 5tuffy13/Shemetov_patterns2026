from Src.Core.abstract_reference import abstract_reference
from Src.Core.abstract_report import abstract_report
from Src.Core.exception import argument_exception
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model


class text_report(abstract_report):
    """
    Реализация текстового представления отчета (TXT)
    """

    def build(self, source: abstract_reference) -> report_result_dto:
        """
        Формирование структурированного текстового отчета
        """
        validator.validate_type(source, abstract_reference, field_name="source")

        if isinstance(source, receipt_model):
            header = "Код | Наименование | Брутто | Нетто "
            data = ""
            for row in source.rows:
                code = row.id
                name = row.name
                gross = row.gross
                net = row.net
                data += f"\n{code} | {name} | {gross} | {net}"
            text = f"{header}{data}"
        elif isinstance(source, nomenclature_model):
            range_name = source.range.name if source.range else ""
            group_name = source.group.name if source.group else ""
            text = (
                f"Номенклатура: {source.name}\n"
                f"Код: {source.id}\n"
                f"Полное наименование: {source.full_name}\n"
                f"Группа: {group_name}\n"
                f"Единица измерения: {range_name}"
            )
        elif isinstance(source, range_model):
            base_name = source.base_range.name if source.base_range else "—"
            text = (
                f"Единица измерения: {source.name}\n"
                f"Код: {source.id}\n"
                f"Коэффициент: {source.coeff}\n"
                f"Базовая единица: {base_name}"
            )
        else:
            raise argument_exception("source", f"Формирование отчета для типа '{type(source).__name__}' не поддерживается!")

        result = report_result_dto()
        result.text = text
        return result
