#!/bin/sh
set -e

if [ ! -f .env ]; then
    cp .env.example .env
    echo "Создан .env из .env.example"
fi

docker compose up --build -d

echo "Ожидание готовности API..."
for i in $(seq 1 30); do
    if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/ | grep -q "200"; then
        break
    fi
    sleep 1
done

echo "Создание демо-пользователя и тестовых данных..."
docker compose exec -T web python manage.py shell <<'EOF'
from datetime import date
from django.contrib.auth import get_user_model
from cats.models import Cat, Travel, TravelStop, TravelChecklistItem

User = get_user_model()
user, created = User.objects.get_or_create(
    username='demo',
    defaults={'first_name': 'Демо', 'last_name': 'Пользователь'},
)
user.set_password('Demo1234!')
user.is_staff = True
user.is_superuser = True
user.save()

cat, _ = Cat.objects.get_or_create(
    name='Marta', owner=user,
    defaults={'color': 'Ginger', 'birth_year': 2022},
)

travel, _ = Travel.objects.get_or_create(
    cat=cat, title='Летняя поездка',
    defaults={
        'destination': 'Казань',
        'start_date': date(2026, 6, 1),
        'end_date': date(2026, 6, 5),
        'transport': 'поезд',
        'status': 'planned',
        'is_public': True,
        'notes': 'Взять переноску и любимый плед.',
    },
)

TravelStop.objects.get_or_create(
    travel=travel, order=1,
    defaults={
        'city': 'Казань',
        'country': 'Россия',
        'address': 'ул. Баумана, 1',
        'arrival_date': date(2026, 6, 1),
        'departure_date': date(2026, 6, 5),
        'notes': 'Отель разрешает проживание с животными.',
    },
)

TravelChecklistItem.objects.get_or_create(
    travel=travel, title='Получить ветеринарную справку',
    defaults={'is_done': False, 'due_date': date(2026, 5, 30)},
)

print(f'Пользователь: demo / Demo1234!')
print(f'Котик: {cat.name} (id={cat.id})')
print(f'Путешествие: {travel.title} (id={travel.id})')
EOF

echo ""
echo "Контейнер запущен."
echo "API:        http://127.0.0.1:8001/"
echo "Админка:    http://127.0.0.1:8001/admin/"
echo ""
echo "Демо-вход:"
echo "  логин:    demo"
echo "  пароль:   Demo1234!"
echo ""
echo "Быстрая проверка через curl:"
echo "  curl http://127.0.0.1:8001/travels/"
echo ""
echo "Логи:    docker compose logs -f web"
echo "Статус:  docker compose ps"
echo "Стоп:    ./stop.sh"
