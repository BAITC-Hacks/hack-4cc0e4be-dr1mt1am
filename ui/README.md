# Аким на 5 часов — frontend

Изолированное React + TypeScript + Vite приложение. Все команды выполняются из `ui/`.

```powershell
npm install
npm run dev
npm run typecheck
npm run build
npm run preview
npm test
```

Node.js 22.18+ (или 24+) нужен для проверки TypeScript-каталога средствами Node. Для Vite см. https://vite.dev/guide/.

## Границы

- `src/data/catalog.ts` — временное зеркало `../engine/data.py` и констант, позже заменяется `GET /api/catalog`.
- Выбор сохраняется в памяти вкладки, после перезагрузки сбрасывается.
- UI считает только стоимость и количество. Направления, несовместимости и окончательная валидация принадлежат Python validator.
- `Decision[]` использует `initiative_id` и `district`; для городского мероприятия `district: null`.
- Симуляция и AI не подключены. Кнопка показывает уведомление без вымышленного результата.
- Исходный Score — предоставленный fixture 52.55768, отображение 52.56.
- Radar — описательное простое среднее 10 baseline значений каждого направления (2 показателя × 5 районов). Это не оценка engine и не формула Score. Метод указан в UI.

## Локальные изображения

Поместите изображения в `public/images/initiatives/m1.webp` … `m14.webp` и добавьте нужной записи каталога `image: '/images/initiatives/m1.webp'`. `InitiativeVisual` использует CSS/Lucide placeholder, если изображение не задано или не загрузилось. Внешние изображения и шрифты не загружаются.

## Структура

- `components/Overview.tsx`: sidebar, hero, метрики, районы и легенда.
- `components/CityRadar.tsx`: диаграмма, загружаемая отдельным модулем.
- `components/Initiatives.tsx`: карточки, visual, фильтры и панель сценария.
- `App.tsx`: состояние и связывание компонентов.
- `utils/presentation.ts`: уровни отображения и описательные данные радара.
- `checks/catalog.test.mjs`: проверка числового зеркала против Python-источника без запуска или изменения backend.
- `checks/render.test.mjs`: smoke-проверка React-разметки, исходных значений и доступности начальных контролов.

Сборка использует TypeScript strict. Отдельный ESLint не настроен. Никаких backend-изменений для запуска UI не требуется.
