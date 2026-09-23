# HTTP adapter

`api.app:app` — FastAPI поверх существующих Python engine и AI. API не содержит
формул, дубликата каталога или бизнес-валидации. `schemas.py` проверяет только
форму JSON, `serializers.py` создаёт независимые JSON-снимки без округления.

| Endpoint | Назначение |
| --- | --- |
| `GET /api/health` | `{"status":"ok"}` |
| `GET /api/catalog` | Статические данные engine и baseline через существующий scoring |
| `POST /api/simulate` | `Decision[]` → `simulate_scenario` → JSON |
| `POST /api/analyze` | `Decision[]` → `simulate_scenario` → `analyze_simulation` |

Оба POST принимают только объект `decisions`, например эталон:

```json
{"decisions":[{"initiative_id":"M7","district":"Nura"},{"initiative_id":"M8","district":"Nura"},{"initiative_id":"M10","district":"Nura"},{"initiative_id":"M12","district":null},{"initiative_id":"M5","district":"Saryarka"}]}
```

Числа от клиента (Score и другие результаты) не принимаются. Неизвестные ID
поступают существующему validator. Невалидный сценарий возвращает HTTP 200 с
`valid: false`, массивом `errors`, бюджетом и без Score; OpenAI не вызывается.
Некорректная форма JSON возвращает HTTP 422 и `error: {code, message}`.

Успешная симуляция возвращает полный снимок `SimulationResult`: в том числе
до/после, дельты и вложенные `triggered_synergies`. API сохраняет точность;
React округляет только отображение, существующий AI layer готовит свой payload.
Успешный анализ возвращает `summary`, `strengths`, `risks`, `tradeoffs`,
`recommendations`. Без ключа — HTTP 503 с кодом `API_KEY_MISSING`; обработанная
ошибка AI — HTTP 502 с безопасным сообщением. Произвольное содержимое исключения
и HTTP headers провайдера не передаются клиенту.

Запуск из корня: `python -m uvicorn api.app:app --reload --port 8000`.
`OPENAI_API_KEY`, `OPENAI_MODEL`, `FRONTEND_ORIGIN` читаются из окружения Python.
По умолчанию CORS разрешён только для `http://localhost:5173`.
Конфигурация API создаётся при старте; после изменения origin нужен перезапуск.

Контракт проверяется в `tests/test_api.py` через TestClient. Анализатор подменяется
в тестах успеха, а конструктор OpenAI заблокирован во всём наборе API-тестов.
