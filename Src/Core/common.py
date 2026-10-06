from Src.Core.validator import argument_exception


class common:
    """
    Набор общих статических методов для интроспекции и работы с моделями
    """

    @staticmethod
    def get_fields(source, is_common: bool = False) -> list:
        """
        Получить полный список свойств (@property) любой модели
            - is_common = True - исключить из списка словари и списки
        """
        if source is None:
            raise argument_exception("Некорректно переданы аргументы: source не может быть None")

        items = list(filter(lambda x: not x.startswith("_"), dir(source)))
        result = []

        for item in items:
            attribute = getattr(source.__class__, item, None)
            if isinstance(attribute, property):
                value = getattr(source, item, None)

                # Исключаем составные контейнеры (dict, list), если запрошены только простые типы
                if is_common and (isinstance(value, dict) or isinstance(value, list)):
                    continue

                result.append(item)

        return result
