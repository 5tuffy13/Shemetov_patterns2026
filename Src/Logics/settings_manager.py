import json
import os
from pathlib import Path
from Src.Core.abstract_manager import abstract_manager
from Src.Core.validator import validator, operation_exception, argument_exception
from Src.Models.settings_model import settings_model
from Src.Models.organization_model import organization_model


class settings_manager(abstract_manager):
    """
    Менеджер для работы с настройками приложения (Singleton)
    """

    __default_file_name: str = "settings.json"
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(settings_manager, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        super().__init__()
        self.__settings: settings_model = settings_model()
        self._initialized = True

    def _resolve_file_path(self, file_name: str) -> Path:
        """
        Поиск пути к файлу: абсолютный, относительный к CWD или к корню репозитория
        """
        path = Path(file_name)
        if path.is_file():
            return path

        # Корень репозитория (Src/Logics -> ../..)
        repo_root = Path(__file__).resolve().parent.parent.parent
        candidate = repo_root / file_name
        if candidate.is_file():
            return candidate

        return path

    def load(self, file_name: str = "") -> None:
        """
        Загрузка и парсинг настроек из JSON-файла
        """
        validator.validate_type(file_name, str, field_name="file_name")
        inner_file_name = file_name.strip() if file_name.strip() else self.__default_file_name

        resolved_path = self._resolve_file_path(inner_file_name)
        if not resolved_path.is_file():
            self.is_loaded = False
            raise operation_exception(
                f"Ошибка при загрузке и обработке файла: {inner_file_name}. Детали: Файл не найден: {resolved_path}"
            )

        try:
            with open(resolved_path, "r", encoding="utf-8") as file:
                self._data = json.load(file)
            self._file_name = str(resolved_path)
            self.is_loaded = self.convert()
        except Exception as ex:
            self.is_loaded = False
            raise operation_exception(
                f"Ошибка при загрузке и обработке файла: {inner_file_name}. Детали: {ex}"
            )

    def convert(self) -> bool:
        """
        Обработка загруженных сырых данных и заполнение модели settings_model
        """
        if not isinstance(self._data, dict):
            raise operation_exception("Некорректная структура данных настроек: ожидается словарь (JSON-объект)")

        try:
            company_data = self._data.get("company") or self._data.get("organization")
            if not company_data or not isinstance(company_data, dict):
                raise operation_exception("В настройках отсутствует обязательная секция 'company'")

            org = organization_model(
                name=str(company_data.get("name", "")),
                inn=str(company_data.get("inn", "")),
                bik=str(company_data.get("bik", "")),
                account=str(company_data.get("account", "")),
                ownership_form=str(company_data.get("ownership_form", company_data.get("ownership", ""))),
            )
            self.__settings.company = org

            boss = self._data.get("boss_name")
            if boss is not None:
                self.__settings.boss_name = str(boss)

            accountant = self._data.get("account_name")
            if accountant is not None:
                self.__settings.account_name = str(accountant)

            if "is_first_start" in self._data:
                self.__settings.is_first_start = bool(self._data["is_first_start"])

            return True
        except Exception as ex:
            raise operation_exception(f"Ошибка при конвертации настроек: {ex}")

    @property
    def settings(self) -> settings_model:
        """
        Модель настроек
        """
        return self.__settings
