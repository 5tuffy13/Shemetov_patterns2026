import json
from pathlib import Path
from Src.Core.abstract_manager import abstract_manager
from Src.Core.event_type_enum import event_type_enum
from Src.Core.log_level_enum import log_level_enum
from Src.Core.validator import validator, operation_exception
from Src.Logics.convertor import convertor
from Src.Logics.observer import observer
from Src.Models.settings_model import settings_model


class settings_manager(abstract_manager):
    """
    Менеджер настроек приложения на базе десериализатора (Singleton)
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

        repo_root = Path(__file__).resolve().parent.parent.parent
        target_path = repo_root / file_name
        if target_path.is_file():
            return target_path

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
            observer().notify(
                event_type_enum.SETTINGS_ERROR,
                {
                    "subsystem": "settings_manager",
                    "level": log_level_enum.ERROR,
                    "message": f"Ошибка загрузки настроек '{inner_file_name}': файл не найден ({resolved_path})",
                },
            )
            raise operation_exception(
                f"Ошибка при загрузке и обработке файла: {inner_file_name}. Детали: Файл не найден: {resolved_path}"
            )

        try:
            with open(resolved_path, "r", encoding="utf-8") as file:
                self._data = json.load(file)
            self._file_name = str(resolved_path)
            self.is_loaded = self.convert()
            observer().notify(
                event_type_enum.LOAD_SETTINGS,
                {
                    "subsystem": "settings_manager",
                    "level": log_level_enum.INFO,
                    "message": f"Загружены настройки из файла '{resolved_path.name}'",
                },
            )
        except Exception as ex:
            self.is_loaded = False
            observer().notify(
                event_type_enum.SETTINGS_ERROR,
                {
                    "subsystem": "settings_manager",
                    "level": log_level_enum.ERROR,
                    "message": f"Ошибка загрузки настроек '{inner_file_name}': {ex}",
                },
            )
            raise operation_exception(
                f"Ошибка при загрузке и обработке файла: {inner_file_name}. Детали: {ex}"
            )

    def convert(self) -> bool:
        """
        Десериализация настроек через общий фасад convertor
        """
        if not isinstance(self._data, dict):
            raise operation_exception("Некорректная структура данных настроек: ожидается словарь (JSON-объект)")

        company_data = self._data.get("company") or self._data.get("organization")
        if not company_data or not isinstance(company_data, dict):
            raise operation_exception("В настройках отсутствует обязательная секция 'company'")

        try:
            worker = convertor()
            restored = worker.deserialize(self._data, target_type=settings_model)
            if not isinstance(restored, settings_model):
                raise operation_exception("Не удалось преобразовать настройки в settings_model")

            self.__settings = restored
            return True
        except Exception as ex:
            raise operation_exception(f"Ошибка при конвертации настроек: {ex}")

    def update_settings(self, new_settings: settings_model) -> None:
        """
        Применить новую модель настроек приложения и оповестить наблюдателей
        """
        validator.validate_type(new_settings, settings_model, field_name="new_settings")
        self.__settings = new_settings
        self.is_loaded = True
        observer().notify(
            event_type_enum.CHANGE_SETTINGS,
            {
                "subsystem": "settings_manager",
                "level": log_level_enum.INFO,
                "message": f"Обновлены настройки приложения (формат ответа: {new_settings.response_format.name})",
            },
        )

    @property
    def settings(self) -> settings_model:
        """
        Модель настроек
        """
        return self.__settings
