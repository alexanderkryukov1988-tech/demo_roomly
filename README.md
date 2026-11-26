## Запуск автотестов

Для запуска нужен Docker с Docker Compose v2. Python и браузер отдельно устанавливать не нужно.

Из корня репозитория выполните:

```bash
docker compose run --build --rm tests
```

Команда соберёт тестовый образ, установит зависимости и запустит smoke-тест вместе с тестами кандидата. Результаты сохраняются в каталоге `artifacts/`:

- `artifacts/junit.xml` — отчёт о выполнении;
- `artifacts/browser/` — скриншоты и trace при падении тестов.

Если Docker недоступен, зависимости можно установить вручную:

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
python -m pytest
```

## Что реализовано

- `locators/` — JSON-локаторы формы, `pages/` — page object, `tests/data/` — тестовые данные.
- `tests/test_booking.py` — три теста задания: позитивный, негативный и проверка дефекта через `xfail(strict=True, reason="BUG-01: ...", raises=AssertionError)`.
- `tests/test_checklist.py` — 33 теста по чек-листу, имена совпадают с пунктами CL-01…CL-33.
- `docs/checklist.md` — чек-лист с результатами прогона, `docs/checklist.xlsx` — то же с подсветкой статусов.
- `docs/bugs.md` — 5 дефектов, скриншоты в `docs/images/`.
- `docs/report.md` — окружение, запуск, проверенные области, ограничения, время и использование ИИ.
