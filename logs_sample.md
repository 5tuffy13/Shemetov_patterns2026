# Журнал событий

| Период | Подсистема | Уровень | Сообщение |
| :--- | :--- | :---: | :--- |
| 2026-11-26T09:45:24.800207 | settings_manager | INFO | Загружены настройки из файла 'settings.json' |
| 2026-11-26T09:45:24.801310 | storage_manager | INFO | Хранилище инициализировано: категорий=6, записей=40 |
| 2026-11-26T09:45:24.834924 | settings_manager | INFO | Обновлены настройки приложения (формат ответа: MARKDOWN) |
| 2026-11-26T09:45:24.835120 | settings_manager | ERROR | Ошибка загрузки настроек 'missing_config_sample.json': файл не найден (missing_config_sample.json) |
| 2026-11-26T09:45:24.835222 | warehouse | INFO | Проведена транзакция id=50bfa0ad-6707-4759-8a40-6ea62f64b1ad: склад='Главный склад', номенклатура='Сахар', объем=2500.0 |
| 2026-11-26T09:45:24.835726 | web_api | DEBUG | Входящий запрос GET /api/entities/storage |
| 2026-11-26T09:45:24.836120 | web_api | INFO | GET /api/entities/storage -> 200 (0.39 ms) |
| 2026-11-26T09:45:24.836630 | web_api | DEBUG | Входящий запрос POST /api/entities/storage |
| 2026-11-26T09:45:24.837239 | storage_manager | INFO | Добавлена сущность в категорию 'storage_key': id=8e67a1a1-d4a6-4f15-aa34-248ea335fa3c, name='Временный склад поставки' |
| 2026-11-26T09:45:24.837365 | web_api | INFO | POST /api/entities/storage -> 201 (0.75 ms) |
| 2026-11-26T09:45:24.837751 | web_api | DEBUG | Входящий запрос PUT /api/entities/storage/8e67a1a1-d4a6-4f15-aa34-248ea335fa3c |
| 2026-11-26T09:45:24.838333 | storage_manager | INFO | Обновлена сущность в категории 'storage_key': id=8e67a1a1-d4a6-4f15-aa34-248ea335fa3c, name='Склад поставки обновленный' |
| 2026-11-26T09:45:24.838452 | web_api | INFO | PUT /api/entities/storage/8e67a1a1-d4a6-4f15-aa34-248ea335fa3c -> 200 (0.7 ms) |
| 2026-11-26T09:45:24.838806 | web_api | DEBUG | Входящий запрос DELETE /api/entities/storage/8e67a1a1-d4a6-4f15-aa34-248ea335fa3c |
| 2026-11-26T09:45:24.843910 | storage_manager | INFO | Удалена сущность из категории 'storage_key': id=8e67a1a1-d4a6-4f15-aa34-248ea335fa3c, name='Склад поставки обновленный' |
| 2026-11-26T09:45:24.844052 | web_api | INFO | DELETE /api/entities/storage/8e67a1a1-d4a6-4f15-aa34-248ea335fa3c -> 200 (5.24 ms) |
| 2026-11-26T09:45:24.844513 | web_api | DEBUG | Входящий запрос DELETE /api/entities/nomenclature_model/369a1641-dc93-4d39-82d7-ed77ebb2680e |
| 2026-11-26T09:45:24.846353 | web_api | ERROR | DELETE /api/entities/nomenclature_model/369a1641-dc93-4d39-82d7-ed77ebb2680e -> 409 (1.84 ms) |
| 2026-11-26T09:45:24.846731 | web_api | DEBUG | Входящий запрос POST /api/osv/filter |
| 2026-11-26T09:45:24.846896 | warehouse | INFO | Сформирована ОСВ: строк=4, период=-..- |
| 2026-11-26T09:45:24.847038 | web_api | INFO | POST /api/osv/filter -> 200 (0.31 ms) |
| 2026-11-26T09:45:24.847330 | web_api | DEBUG | Входящий запрос GET /api/logs/export |
| 2026-11-26T09:45:24.848162 | web_api | INFO | GET /api/logs/export -> 200 (0.83 ms) |
| 2026-11-26T09:45:24.848484 | web_api | DEBUG | Входящий запрос GET /api/logs/export |