# Проверочные запросы для Postman и curl

Готовая Postman-коллекция для сценария “Кото-путешествия” находится в файле
`KITTY_TRAVELS_POSTMAN_COLLECTION.json`. Ниже приведены те же проверки в формате
curl, чтобы их можно было повторить без Postman.

Ниже используется переменная:

```bash
TOKEN=<access_token>
```

## 1. Получить JWT-токен

```bash
curl -X POST http://127.0.0.1:8000/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{"username":"tester","password":"testpass123"}'
```

Ожидаемый результат: `200 OK`, в ответе поля `refresh` и `access`.

## 2. Получить список котиков

```bash
curl http://127.0.0.1:8000/cats/ \
  -H "Authorization: Bearer $TOKEN"
```

Ожидаемый результат: `200 OK`, список котиков или пагинированный ответ с `count` и `results`.

## 3. Создать котика

```bash
curl -X POST http://127.0.0.1:8000/cats/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Barsik",
    "color": "White",
    "birth_year": 2021
  }'
```

Ожидаемый результат: `201 Created`, в ответе данные нового котика.

## 4. Поставить лайк котику

```bash
curl -X POST http://127.0.0.1:8000/cats/1/like/ \
  -H "Authorization: Bearer $TOKEN"
```

Ожидаемый результат: `201 Created`, в ответе объект лайка и вложенные данные котика.

## 5. Проверить ошибку повторного лайка

```bash
curl -X POST http://127.0.0.1:8000/cats/1/like/ \
  -H "Authorization: Bearer $TOKEN"
```

Ожидаемый результат: `400 Bad Request`, ответ:

```json
{
  "detail": [
    "Вы уже лайкнули этого котика."
  ]
}
```

## 6. Добавить котика в избранное

```bash
curl -X POST http://127.0.0.1:8000/cats/1/favorite/ \
  -H "Authorization: Bearer $TOKEN"
```

Ожидаемый результат: `201 Created`.

## 7. Получить мои лайки

```bash
curl http://127.0.0.1:8000/cats/my_likes/ \
  -H "Authorization: Bearer $TOKEN"
```

Ожидаемый результат: `200 OK`, список лайкнутых котиков текущего пользователя.

## 8. Получить топ котиков по лайкам

```bash
curl http://127.0.0.1:8000/cats/top/ \
  -H "Authorization: Bearer $TOKEN"
```

Ожидаемый результат: `200 OK`, список котиков, отсортированный по `likes_count`.

## 9. Убрать лайк

```bash
curl -X DELETE http://127.0.0.1:8000/cats/1/unlike/ \
  -H "Authorization: Bearer $TOKEN"
```

Ожидаемый результат: `204 No Content`.

## 10. Получить мое избранное

```bash
curl http://127.0.0.1:8000/cats/my_favorites/ \
  -H "Authorization: Bearer $TOKEN"
```

Ожидаемый результат: `200 OK`, список котиков из избранного.

## Что удобно приложить в отчет

- получение токена;
- успешное создание котика;
- успешный лайк;
- ошибка повторного лайка;
- список `my_likes`;
- список `top`.

# Проверочные запросы для сценария “Кото-путешествия”

Ниже используется переменная:

```bash
TOKEN=<access_token>
```

## 11. Создать котика для путешествия

```bash
curl -X POST http://127.0.0.1:8000/cats/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Marta",
    "color": "Ginger",
    "birth_year": 2022
  }'
```

Ожидаемый результат: `201 Created`. Сохраните `id` котика как `CAT_ID`.

## 12. Создать путешествие

```bash
curl -X POST http://127.0.0.1:8000/travels/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cat": 1,
    "title": "Летняя поездка",
    "destination": "Казань",
    "start_date": "2026-06-01",
    "end_date": "2026-06-05",
    "transport": "поезд",
    "status": "planned",
    "is_public": true,
    "notes": "Взять переноску и любимый плед."
  }'
```

Ожидаемый результат: `201 Created`. Сохраните `id` путешествия как `TRAVEL_ID`.

## 13. Получить список путешествий

```bash
curl http://127.0.0.1:8000/travels/ \
  -H "Authorization: Bearer $TOKEN"
```

Ожидаемый результат: `200 OK`, список своих и публичных путешествий.

## 14. Получить только мои путешествия

```bash
curl http://127.0.0.1:8000/travels/my/ \
  -H "Authorization: Bearer $TOKEN"
```

Ожидаемый результат: `200 OK`, список путешествий котиков текущего пользователя.

## 15. Добавить точку маршрута

```bash
curl -X POST http://127.0.0.1:8000/travel-stops/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "travel": 1,
    "order": 1,
    "city": "Казань",
    "country": "Россия",
    "address": "ул. Баумана, 1",
    "arrival_date": "2026-06-01",
    "departure_date": "2026-06-05",
    "notes": "Отель разрешает проживание с животными."
  }'
```

Ожидаемый результат: `201 Created`.

## 16. Проверить ошибку повторного номера точки

```bash
curl -X POST http://127.0.0.1:8000/travel-stops/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "travel": 1,
    "order": 1,
    "city": "Иннополис",
    "country": "Россия",
    "arrival_date": "2026-06-02",
    "departure_date": "2026-06-03"
  }'
```

Ожидаемый результат: `400 Bad Request`, ответ содержит поле `order`.

## 17. Добавить задачу в чек-лист

```bash
curl -X POST http://127.0.0.1:8000/travel-checklist/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "travel": 1,
    "title": "Получить ветеринарную справку",
    "due_date": "2026-05-30"
  }'
```

Ожидаемый результат: `201 Created`.

## 18. Отметить задачу выполненной

```bash
curl -X PATCH http://127.0.0.1:8000/travel-checklist/1/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_done": true
  }'
```

Ожидаемый результат: `200 OK`, поле `is_done` равно `true`.

## 19. Проверить ошибку дат путешествия

```bash
curl -X POST http://127.0.0.1:8000/travels/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cat": 1,
    "title": "Некорректная поездка",
    "destination": "Москва",
    "start_date": "2026-07-10",
    "end_date": "2026-07-01"
  }'
```

Ожидаемый результат: `400 Bad Request`, ответ содержит поле `end_date`.

## 20. Отфильтровать путешествия по статусу

```bash
curl "http://127.0.0.1:8000/travels/?status=planned" \
  -H "Authorization: Bearer $TOKEN"
```

Ожидаемый результат: `200 OK`, список запланированных путешествий.
