class argument_exception(Exception):
    """
    Пользовательское исключение для ошибок валидации аргументов
    """

    def __init__(self, field: str = "", message: str = "", stack_trace: str = ""):
        """
        Инициализация исключения с поддержкой как сообщения, так и пары (поле, сообщение)
        """
        if message:
            self.__field = str(field).strip()
            self.__message = str(message).strip()
        else:
            self.__field = ""
            self.__message = str(field).strip()

        self.__stack_trace = str(stack_trace).strip()
        if self.__field:
            super().__init__(f"Ошибка аргумента '{self.__field}': {self.__message}")
        else:
            super().__init__(f"Ошибка аргумента: {self.__message}")

    @property
    def field(self) -> str:
        """
        Имя поля, вызвавшего исключение
        """
        return self.__field

    @property
    def message(self) -> str:
        """
        Сообщение об ошибке
        """
        return self.__message

    @property
    def stack_trace(self) -> str:
        """
        Трассировка стека вызовов
        """
        return self.__stack_trace


class operation_exception(Exception):
    """
    Пользовательское исключение для ошибок выполнения операций
    """

    def __init__(self, message: str = ""):
        """
        Инициализация исключения операции
        """
        self.__message = str(message).strip()
        super().__init__(f"Ошибка операции: {self.__message}")

    @property
    def message(self) -> str:
        """
        Сообщение об ошибке
        """
        return self.__message
