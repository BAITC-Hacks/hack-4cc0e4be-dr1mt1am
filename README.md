# hack-4cc0e4be-dr1mt1am
Hackathon team repository for dr1mt1am

## AI smoke test

Ручная проверка настоящего OpenAI API на эталонном сценарии. Запускайте из корня
репозитория в окружении с установленными зависимостями из `requirements.txt`.
В PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
$env:OPENAI_API_KEY="your-api-key"
$env:OPENAI_MODEL="gpt-5.6-terra"
python scripts/ai_smoke_test.py
```

`OPENAI_MODEL` необязателен: по умолчанию AI layer использует `gpt-5.6-terra`.
Ответ запрашивается на русском языке. Скрипт выводит рассчитанные движком значения,
название модели и разделы AI-анализа. Без ключа запрос не выполняется, выводится
сообщение об отсутствующем `OPENAI_API_KEY`, код завершения — `2`.
Другие коды ошибок: `1` — невалидная/неполная симуляция, `3` — ошибка запроса,
`4` — некорректный ответ AI; успешный запуск возвращает `0`.

Переменные читаются только из окружения; `.env.example` служит примером,
файл `.env` автоматически не загружается. Удалить ключ из текущей сессии PowerShell:

```powershell
Remove-Item Env:OPENAI_API_KEY
```

Unit tests работают без сети и не выполняют реальные API-запросы.
Ручной smoke test находится вне `tests/` и не запускается этой командой:

```powershell
python -B -m unittest discover -s tests
```

## Optional features

The `features` package is deliberately independent from the simulation core:

- `features.events` applies unexpected events and optional responses without mutating a simulation result.
- `features.events.DEFAULT_EVENTS` contains four ready-to-demo event definitions.
- `features.comparison` converts scored scenarios into stable table rows for a UI or API.
- `features.optimization` exhaustively evaluates valid decision combinations through injected `validator`, `simulator`, and `scorer` callbacks.

Run the focused tests with:

```powershell
python -m unittest discover -s tests -v
```
