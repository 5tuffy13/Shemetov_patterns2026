from typing import Any, Dict
from Src.Core.abstract_dto import abstract_dto
from Src.Core.validator import validator


class osv_row_dto(abstract_dto):
    """
    Строка Оборотно-сальдовой ведомости (ОСВ) по номенклатуре и складу
    """

    def __init__(
        self,
        storage_name: str = "",
        storage_id: str = "",
        nomenclature_name: str = "",
        nomenclature_id: str = "",
        range_name: str = "",
        start_balance: float = 0.0,
        income: float = 0.0,
        outcome: float = 0.0,
        end_balance: float = 0.0,
    ):
        """
        Инициализация строки оборотно-сальдовой ведомости
        """
        super().__init__()
        self.storage_name: str = str(storage_name).strip()
        self.storage_id: str = str(storage_id).strip()
        self.nomenclature_name: str = str(nomenclature_name).strip()
        self.nomenclature_id: str = str(nomenclature_id).strip()
        self.range_name: str = str(range_name).strip()
        self.start_balance: float = float(start_balance)
        self.income: float = float(income)
        self.outcome: float = float(outcome)
        self.end_balance: float = float(end_balance)

    def from_domain_model(self, source: Any) -> "osv_row_dto":
        """
        Создать DTO из доменной модели
        """
        return self

    def from_dict(self, data: Dict[str, Any]) -> "osv_row_dto":
        """
        Заполнить поля DTO из словаря
        """
        validator.validate_type(data, dict, field_name="data")
        self.storage_name = str(data.get("storage_name", ""))
        self.storage_id = str(data.get("storage_id", ""))
        self.nomenclature_name = str(data.get("nomenclature_name", ""))
        self.nomenclature_id = str(data.get("nomenclature_id", ""))
        self.range_name = str(data.get("range_name", ""))
        self.start_balance = float(data.get("start_balance", 0.0))
        self.income = float(data.get("income", 0.0))
        self.outcome = float(data.get("outcome", 0.0))
        self.end_balance = float(data.get("end_balance", 0.0))
        return self

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразование строки ведомости в плоский словарь для сериализации
        """
        return {
            "storage_name": self.storage_name,
            "storage_id": self.storage_id,
            "nomenclature_name": self.nomenclature_name,
            "nomenclature_id": self.nomenclature_id,
            "range_name": self.range_name,
            "start_balance": round(self.start_balance, 3),
            "income": round(self.income, 3),
            "outcome": round(self.outcome, 3),
            "end_balance": round(self.end_balance, 3),
        }
