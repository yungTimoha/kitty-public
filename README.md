### Репозиторий

Актуальный URL проекта: [https://github.com/yungTimoha/kitty-public](https://github.com/yungTimoha/kitty-public).

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone https://github.com/yungTimoha/kitty-public.git
```

```bash
cd kittygram2
```

Cоздать и активировать виртуальное окружение:

```bash
python3 -m venv env
```

```bash
source env/bin/activate
```

```bash
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```bash
pip install -r requirements.txt
```

Выполнить миграции:

```bash
python3 manage.py migrate
```

Запустить проект:

```bash
python3 manage.py runserver
```

Перед запуском можно создать файл `.env` на основе шаблона:

```bash
cp .env.example .env
```

### Создание тестового пользователя

После старта проекта нужен хотя бы один пользователь, от имени которого
будут выполняться защищённые запросы к API.

Вариант 1 — суперпользователь (для доступа в админку и API):

```bash
python3 manage.py createsuperuser
```

При запуске в Docker:

```bash
docker compose exec web python manage.py createsuperuser
```

Вариант 2 — обычный пользователь через Djoser:

```bash
curl -X POST http://127.0.0.1:8001/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "password": "Test1234!"}'
```

Получение JWT-токена для тестового пользователя:

```bash
curl -X POST http://127.0.0.1:8001/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "password": "Test1234!"}'
```

В ответе будет JSON с полями `access` и `refresh`. Полученный `access`-токен
подставляется в заголовок `Authorization: Bearer <access_token>` для всех
защищённых запросов из раздела API ниже.

### Основные эндпоинты API

- `GET /cats/` - список котиков с фильтрами `color`, `owner`, `search`
- `POST /cats/` - создать котика
- `GET /cats/{id}/` - получить котика
- `POST /cats/{id}/like/` - лайкнуть котика
- `DELETE /cats/{id}/unlike/` - убрать лайк
- `POST /cats/{id}/favorite/` - добавить в избранное
- `DELETE /cats/{id}/unfavorite/` - убрать из избранного
- `GET /cats/my_likes/` - мои лайкнутые котики
- `GET /cats/my_favorites/` - мои избранные котики
- `GET /cats/top/` - топ котиков по лайкам
- `GET /likes/` - список моих лайков
- `GET /favorites/` - список моего избранного

Проверочные curl-запросы собраны в `API_CHECK_REQUESTS.md`. Postman-коллекция
для сценария "Кото-путешествия" находится в
`KITTY_TRAVELS_POSTMAN_COLLECTION.json`.

Диаграммы для курсовой работы подготовлены в папке `docs/`:

- `docs/use_case_diagram.md` - диаграмма вариантов использования;
- `docs/deployment_diagram.md` - диаграмма развёртывания Docker-варианта.

В этих файлах есть SVG-изображения диаграмм и Mermaid-исходники.

### Кото-путешествия

Функциональность “Кото-путешествия” позволяет планировать поездки для своих
котиков, вести маршрут по точкам и хранить чек-лист подготовки.

#### Модели

| Модель | Назначение | Ключевые поля |
|---|---|---|
| `Travel` | Путешествие котика | `cat`, `title`, `destination`, `start_date`, `end_date`, `status`, `is_public` |
| `TravelStop` | Точка маршрута | `travel`, `order`, `city`, `country`, `arrival_date`, `departure_date` |
| `TravelChecklistItem` | Задача подготовки | `travel`, `title`, `is_done`, `due_date` |

Статусы путешествия: `planned`, `in_progress`, `completed`, `cancelled`.

#### API путешествий

| № | URL | Метод | Назначение | Права доступа | Тело запроса | Коды ответов | Примечания/валидации |
|---|---|---|---|---|---|---|---|
| 1 | `/travels/` | `GET` | Получить свои и публичные путешествия | Авторизованный пользователь | - | `200`, `401` | Поддерживает фильтры `cat`, `status`, `destination`, `is_public` |
| 2 | `/travels/` | `POST` | Создать путешествие для котика | Владелец котика | `cat`, `title`, `destination`, `start_date`, `end_date`, `transport`, `status`, `is_public`, `notes` | `201`, `400`, `401` | Нельзя создать путешествие для чужого котика; `end_date` не раньше `start_date` |
| 3 | `/travels/{id}/` | `GET` | Получить путешествие | Владелец или публичное путешествие | - | `200`, `401`, `404` | Приватные чужие путешествия не попадают в queryset |
| 4 | `/travels/{id}/` | `PATCH` | Частично изменить путешествие | Только владелец котика | Любые изменяемые поля путешествия | `200`, `400`, `401`, `403`, `404` | Новые даты не должны конфликтовать с точками маршрута |
| 5 | `/travels/{id}/` | `DELETE` | Удалить путешествие | Только владелец котика | - | `204`, `401`, `403`, `404` | Вместе с путешествием удаляются точки и чек-лист |
| 6 | `/travels/my/` | `GET` | Получить только свои путешествия | Авторизованный пользователь | - | `200`, `401` | Удобный личный список текущего пользователя |
| 7 | `/travel-stops/` | `GET` | Получить точки маршрута | Авторизованный пользователь | - | `200`, `401` | Видны точки своих и публичных путешествий; фильтр `travel` |
| 8 | `/travel-stops/` | `POST` | Добавить точку маршрута | Владелец путешествия | `travel`, `order`, `city`, `country`, `address`, `arrival_date`, `departure_date`, `notes` | `201`, `400`, `401` | `order` уникален внутри путешествия; даты точки внутри дат путешествия |
| 9 | `/travel-stops/{id}/` | `PATCH` | Изменить точку маршрута | Владелец путешествия | Любые изменяемые поля точки | `200`, `400`, `401`, `403`, `404` | Чужие точки нельзя менять |
| 10 | `/travel-stops/{id}/` | `DELETE` | Удалить точку маршрута | Владелец путешествия | - | `204`, `401`, `403`, `404` | Удаляется только выбранная точка |
| 11 | `/travel-checklist/` | `GET` | Получить задачи подготовки | Владелец путешествия | - | `200`, `401` | Видны только задачи своих путешествий; фильтры `travel`, `is_done` |
| 12 | `/travel-checklist/` | `POST` | Добавить задачу подготовки | Владелец путешествия | `travel`, `title`, `is_done`, `due_date` | `201`, `400`, `401` | `title` уникален внутри путешествия; `due_date` не позже начала путешествия |
| 13 | `/travel-checklist/{id}/` | `PATCH` | Изменить или отметить задачу | Владелец путешествия | `title`, `is_done`, `due_date` | `200`, `400`, `401`, `403`, `404` | Используется для отметки задачи выполненной |
| 14 | `/travel-checklist/{id}/` | `DELETE` | Удалить задачу подготовки | Владелец путешествия | - | `204`, `401`, `403`, `404` | Удаляется только выбранная задача |

#### Фильтрация

- `/travels/?cat=1` - путешествия конкретного котика;
- `/travels/?status=planned` - путешествия по статусу;
- `/travels/?destination=казань` - поиск по направлению;
- `/travels/?is_public=true` - только публичные путешествия;
- `/travel-stops/?travel=1` - точки конкретного путешествия;
- `/travel-checklist/?travel=1` - чек-лист конкретного путешествия;
- `/travel-checklist/?is_done=false` - невыполненные задачи.

#### Валидации

- путешествие можно создать только для своего котика;
- дата окончания путешествия не может быть раньше даты начала;
- точка маршрута должна попадать в даты путешествия;
- дата выезда из точки не может быть раньше даты заезда;
- порядковый номер точки маршрута уникален внутри путешествия;
- срок задачи подготовки должен быть не позже даты начала путешествия;
- название задачи чек-листа уникально внутри путешествия.

#### Примеры JSON

Создание путешествия:

```json
POST /travels/
{
  "cat": 1,
  "title": "Летняя поездка",
  "destination": "Казань",
  "start_date": "2026-06-01",
  "end_date": "2026-06-05",
  "transport": "поезд",
  "status": "planned",
  "is_public": true,
  "notes": "Взять переноску и любимый плед."
}
```

Успешный ответ `201 Created`:

```json
{
  "id": 1,
  "cat": 1,
  "cat_name": "Marta",
  "owner": 1,
  "title": "Летняя поездка",
  "destination": "Казань",
  "start_date": "2026-06-01",
  "end_date": "2026-06-05",
  "transport": "поезд",
  "status": "planned",
  "is_public": true,
  "notes": "Взять переноску и любимый плед.",
  "stops": [],
  "created_at": "2026-05-12T12:00:00Z",
  "updated_at": "2026-05-12T12:00:00Z"
}
```

Создание точки маршрута:

```json
POST /travel-stops/
{
  "travel": 1,
  "order": 1,
  "city": "Казань",
  "country": "Россия",
  "address": "ул. Баумана, 1",
  "arrival_date": "2026-06-01",
  "departure_date": "2026-06-05",
  "notes": "Отель разрешает проживание с животными."
}
```

Успешный ответ `201 Created`:

```json
{
  "id": 1,
  "travel": 1,
  "order": 1,
  "city": "Казань",
  "country": "Россия",
  "address": "ул. Баумана, 1",
  "arrival_date": "2026-06-01",
  "departure_date": "2026-06-05",
  "notes": "Отель разрешает проживание с животными."
}
```

Создание задачи подготовки:

```json
POST /travel-checklist/
{
  "travel": 1,
  "title": "Получить ветеринарную справку",
  "due_date": "2026-05-30"
}
```

Успешный ответ `201 Created`:

```json
{
  "id": 1,
  "travel": 1,
  "title": "Получить ветеринарную справку",
  "is_done": false,
  "due_date": "2026-05-30",
  "created_at": "2026-05-12T12:05:00Z"
}
```

Примеры ошибок:

```json
400 Bad Request
{
  "end_date": [
    "Дата окончания не может быть раньше даты начала."
  ]
}
```

```json
401 Unauthorized
{
  "detail": "Authentication credentials were not provided."
}
```

```json
403 Forbidden
{
  "detail": "You do not have permission to perform this action."
}
```

```json
404 Not Found
{
  "detail": "Not found."
}
```

```json
405 Method Not Allowed
{
  "detail": "Method \"POST\" not allowed."
}
```

Для защищенных эндпоинтов нужен заголовок:

```bash
Authorization: Bearer <access_token>
```

### Локальный запуск в браузере

При локальном запуске в режиме разработки запросы из браузера на `127.0.0.1`
и `localhost` обрабатываются через сессию, поэтому API доступно сразу после
старта сервера.

### Запуск в Docker

1. Создать локальный файл окружения:

```bash
cp .env.example .env
```

2. Проверить Docker Compose конфигурацию:

```bash
docker compose config --quiet
```

3. Собрать и запустить контейнер:

```bash
docker compose up --build
```

Для запуска в фоне:

```bash
docker compose up --build -d
```

4. Проверить состояние контейнера и логи:

```bash
docker compose ps
```

```bash
docker compose logs web
```

5. Проверить доступность API:

```text
http://127.0.0.1:8001/
```

```bash
curl -i http://127.0.0.1:8001/
```

Контейнер при старте автоматически применяет миграции через `entrypoint.sh`.
