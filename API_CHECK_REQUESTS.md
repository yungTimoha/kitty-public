# Проверочные запросы для Postman и curl

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
