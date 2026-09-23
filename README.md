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
