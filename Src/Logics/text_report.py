from Src.Core.abstract_reference import abstract_reference
from Src.Core.abstract_report import abstract_report
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.receipt_model import receipt_model


class text_report(abstract_report):
    """
    Реализация текстового представления отчета по технологической карте
    """

    def __init__(self):
        """
        Инициализация построителя текстового отчета
        """
        self.__receipt: receipt_model = None

    def build(self, source: abstract_reference) -> report_result_dto:
        """
        Формирование текстового отчета по технологической карте блюда
        """
        validator.validate_type(source, receipt_model, field_name="source")
        self.__receipt = source

        header = "Код | Наименование | Брутто | Нетто "
        data = ""

        for row in self.__receipt.rows:
            code = row.id
            name = row.name
            gross = row.gross
            net = row.net
            data += f"\n{code} | {name} | {gross} | {net}"

        result = report_result_dto()
        result.text = f"{header}{data}"
        return result
