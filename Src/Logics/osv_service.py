import datetime
from typing import Any, Dict, List, Optional, Tuple
from Src.Core.validator import validator
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_type_enum import filter_type_enum
from Src.Dtos.osv_row_dto import osv_row_dto
from Src.Logics.prototype import prototype
from Src.Models.transaction_model import transaction_model


class osv_service:
    """
    Сервис формирования Оборотно-сальдовой ведомости (ОСВ) на базе паттерна Прототип
    """

    def __init__(self, storage=None):
        """
        Инициализация сервиса ОСВ с привязкой к хранилищу
        """
        self.__storage = storage

    def build(
        self,
        filter_instance: Optional[filter_dto] = None,
        transactions: Optional[List[transaction_model]] = None,
    ) -> List[osv_row_dto]:
        """
        Формирование оборотно-сальдовой ведомости с применением фильтрации через Прототип
        """
        source_transactions = transactions
        if source_transactions is None:
            if self.__storage is not None:
                source_transactions = self.__storage.transactions
            else:
                source_transactions = []

        # Выделение диапазона дат из фильтра (если передан)
        start_date, end_date, domain_filter = self._parse_period_filters(filter_instance)

        # 1. Применение доменных фильтров через Прототип
        tx_prototype = prototype(source_transactions)
        filtered_prototype = tx_prototype.clone(domain_filter) if domain_filter else tx_prototype

        # 2. Группировка транзакций по ключу (склад, номенклатура)
        # ключ: (storage_id, nomenclature_id) -> данные группы
        groups: Dict[Tuple[str, str], Dict[str, Any]] = {}

        for tx in filtered_prototype.data:
            if not isinstance(tx, transaction_model):
                continue

            storage_id = tx.storage.id if tx.storage else ""
            storage_name = tx.storage.name if tx.storage else "Не указан"
            nom_id = tx.nomenclature.id if tx.nomenclature else ""
            nom_name = tx.nomenclature.name if tx.nomenclature else "Не указана"
            range_name = tx.range.name if tx.range else ""

            group_key = (storage_id, nom_id)
            if group_key not in groups:
                groups[group_key] = {
                    "storage_id": storage_id,
                    "storage_name": storage_name,
                    "nomenclature_id": nom_id,
                    "nomenclature_name": nom_name,
                    "range_name": range_name,
                    "start_balance": 0.0,
                    "income": 0.0,
                    "outcome": 0.0,
                }

            entry = groups[group_key]
            val = tx.value
            tx_period = tx.period

            # Если задан период: до периода -> сальдо, в периоде -> обороты
            if start_date is not None and tx_period < start_date:
                entry["start_balance"] += val
            elif end_date is not None and tx_period > end_date:
                # Транзакции позже окончания периода не включаются в обороты
                continue
            else:
                if val > 0:
                    entry["income"] += val
                else:
                    entry["outcome"] += abs(val)

        # 3. Формирование результирующих DTO строк ведомости
        result: List[osv_row_dto] = []
        for entry in groups.values():
            start_bal = entry["start_balance"]
            inc = entry["income"]
            outc = entry["outcome"]
            end_bal = start_bal + inc - outc

            row = osv_row_dto(
                storage_name=entry["storage_name"],
                storage_id=entry["storage_id"],
                nomenclature_name=entry["nomenclature_name"],
                nomenclature_id=entry["nomenclature_id"],
                range_name=entry["range_name"],
                start_balance=start_bal,
                income=inc,
                outcome=outc,
                end_balance=end_bal,
            )
            result.append(row)

        return result

    def _parse_period_filters(
        self, filter_instance: Optional[filter_dto]
    ) -> Tuple[Optional[datetime.datetime], Optional[datetime.datetime], Optional[filter_dto]]:
        """
        Разделение общего фильтра на временные границы периода и доменные критерии
        """
        if filter_instance is None or len(filter_instance.items) == 0:
            return None, None, None

        start_date: Optional[datetime.datetime] = None
        end_date: Optional[datetime.datetime] = None
        domain_filter = filter_dto()

        for item in filter_instance.items:
            field_clean = item.field_name.lower().strip()
            # Обработка фильтров даты
            if field_clean in ("start_date", "start_period", "date_from") or (
                field_clean == "period" and item.filter_type in (filter_type_enum.GREATER, filter_type_enum.GREATER_OR_EQUAL)
            ):
                start_date = self._parse_date(item.value)
            elif field_clean in ("end_date", "end_period", "date_to") or (
                field_clean == "period" and item.filter_type in (filter_type_enum.LESS, filter_type_enum.LESS_OR_EQUAL)
            ):
                end_date = self._parse_date(item.value)
            else:
                domain_filter.add_item(item)

        return start_date, end_date, domain_filter if len(domain_filter.items) > 0 else None

    def _parse_date(self, val: Any) -> Optional[datetime.datetime]:
        """
        Безопасное приведение значения к типу datetime
        """
        if isinstance(val, datetime.datetime):
            return val
        if isinstance(val, datetime.date):
            return datetime.datetime.combine(val, datetime.time.min)
        if isinstance(val, str):
            clean_str = val.strip()
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d.%m.%Y %H:%M:%S", "%d.%m.%Y"):
                try:
                    return datetime.datetime.strptime(clean_str, fmt)
                except ValueError:
                    pass
        return None
