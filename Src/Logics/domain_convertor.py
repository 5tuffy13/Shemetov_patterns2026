from typing import Any, Dict
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.abstract_dto import abstract_dto
from Src.Core.abstract_mapping_factory import abstract_mapping_factory
from Src.Core.common import common
from Src.Core.exception import argument_exception


class domain_convertor(abstract_convertor):
    """
    Конвертер доменных сущностей через промежуточное преобразование в DTO
    """

    def __init__(
        self,
        convert_factory: abstract_convert_factory,
        mapping_factory: abstract_mapping_factory,
    ):
        super().__init__()
        self.__convert_factory = convert_factory
        self.__mapping_factory = mapping_factory

    @property
    def convert_factory(self) -> abstract_convert_factory:
        return self.__convert_factory

    @property
    def mapping_factory(self) -> abstract_mapping_factory:
        return self.__mapping_factory

    def convert(self, source: Any) -> Any:
        """
        Преобразование доменной сущности в словарь через DTO
        """
        if source is None:
            return None

        # Преобразование в структуру DTO
        dto = self.__mapping_factory.to_dto(source)
        if dto is None:
            raise argument_exception(
                "source",
                f"Невозможно сопоставить тип '{type(source).__name__}' в структуру DTO!"
            )

        if isinstance(dto, (int, float, str, bool)):
            return dto

        if isinstance(dto, (list, tuple, set)):
            return [self.convert(item) for item in dto]

        if not isinstance(dto, abstract_dto):
            # Если объект не является DTO, делегируем в базовую фабрику
            conv = self.__convert_factory.create(type(dto))
            return conv.convert(dto)

        result: Dict[str, Any] = {}
        fields = common.get_fields(dto)

        for field in sorted(fields):
            try:
                value = getattr(dto, field)
            except Exception:
                continue

            if value is None:
                result[field] = None
            elif isinstance(value, (list, tuple, set)):
                result[field] = [self.convert(elem) for elem in value]
            elif isinstance(value, abstract_dto):
                result[field] = self.convert(value)
            else:
                conv = self.__convert_factory.create(type(value))
                result[field] = conv.convert(value)

        return result
