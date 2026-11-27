import sys
from pathlib import Path
from unittest.mock import MagicMock
import pytest

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Core.abstract_observer import abstract_observer
from Src.Core.event_type_enum import event_type_enum
from Src.Core.exception import argument_exception
from Src.Core.log_level_enum import log_level_enum
from Src.Logics.observer import observer


class test_observer:
    """
    Модульные тесты шины событий на базе шаблона Наблюдатель
    """

    @pytest.fixture(autouse=True)
    def setup_observer(self):
        # Подготовка
        self.bus = observer()
        saved_handlers = self.bus.handlers
        self.bus.clear()
        yield
        self.bus.clear()
        for handler in saved_handlers:
            self.bus.add(handler)

    def test_success_observer_add_and_notify(self):
        """
        <summary>
        Проверка подписки наблюдателя и доставки события с переданными параметрами
        </summary>
        """
        # Подготовка
        handler = MagicMock(spec=abstract_observer)
        payload = {"subsystem": "storage_manager", "level": log_level_enum.INFO, "message": "Тестовое событие"}

        # Действие
        self.bus.add(handler)
        self.bus.notify(event_type_enum.ADD_ENTITY, payload)

        # Проверка
        handler.handle.assert_called_once_with(event_type_enum.ADD_ENTITY, payload)

    def test_success_observer_no_duplicate_handlers(self):
        """
        <summary>
        Проверка защиты от повторной регистрации одного и того же наблюдателя
        </summary>
        """
        # Подготовка
        handler = MagicMock(spec=abstract_observer)

        # Действие
        self.bus.add(handler)
        self.bus.add(handler)
        self.bus.notify(event_type_enum.STORAGE_LOADED, {"message": "Загрузка"})

        # Проверка
        assert len(self.bus.handlers) == 1
        assert handler.handle.call_count == 1

    def test_success_observer_delete_stops_notifications(self):
        """
        <summary>
        Проверка прекращения доставки уведомлений после отписки наблюдателя
        </summary>
        """
        # Подготовка
        handler = MagicMock(spec=abstract_observer)
        self.bus.add(handler)

        # Действие
        self.bus.delete(handler)
        self.bus.notify(event_type_enum.DELETE_ENTITY, {"message": "Удаление"})

        # Проверка
        assert len(self.bus.handlers) == 0
        handler.handle.assert_not_called()

    def test_fail_observer_add_invalid_type(self):
        """
        <summary>
        Проверка выброса argument_exception при подписке объекта неподходящего типа
        </summary>
        """
        # Подготовка
        invalid_handler = object()

        # Действие и Проверка
        with pytest.raises(argument_exception):
            self.bus.add(invalid_handler)

    def test_success_observer_isolates_handler_exception(self):
        """
        <summary>
        Проверка изоляции сбоев: исключение в одном наблюдателе не прерывает доставку остальным
        </summary>
        """
        # Подготовка
        failing_handler = MagicMock(spec=abstract_observer)
        failing_handler.handle.side_effect = RuntimeError("Сбой обработчика")
        healthy_handler = MagicMock(spec=abstract_observer)
        self.bus.add(failing_handler)
        self.bus.add(healthy_handler)

        # Действие
        self.bus.notify(event_type_enum.OSV_BUILT, {"message": "Ведомость построена"})

        # Проверка
        failing_handler.handle.assert_called_once()
        healthy_handler.handle.assert_called_once()
