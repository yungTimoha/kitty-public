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

2. Собрать и запустить контейнер:

```bash
docker compose up --build
```

3. Открыть приложение:

```text
http://127.0.0.1:8000/
```

Контейнер при старте автоматически применяет миграции.
