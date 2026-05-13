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

echo "Создание демо-данных..."
docker compose exec -T web python manage.py shell <<'EOF'
from datetime import date
from django.contrib.auth import get_user_model
from cats.models import (Cat, Travel, TravelStop, TravelChecklistItem,
                         Like, Favorite, Achievement)

User = get_user_model()

# --- Пользователи ---
demo, _ = User.objects.get_or_create(
    username='demo',
    defaults={'first_name': 'Демо', 'last_name': 'Пользователь'},
)
demo.set_password('Demo1234!')
demo.is_staff = True
demo.is_superuser = True
demo.save()

viewer, _ = User.objects.get_or_create(
    username='viewer',
    defaults={'first_name': 'Второй', 'last_name': 'Пользователь'},
)
viewer.set_password('Viewer1234!')
viewer.save()

# --- Котики demo ---
marta, _ = Cat.objects.get_or_create(
    name='Marta', owner=demo,
    defaults={'color': 'Ginger', 'birth_year': 2022},
)

simba, _ = Cat.objects.get_or_create(
    name='Simba', owner=demo,
    defaults={'color': 'Black', 'birth_year': 2021},
)

# --- Котик viewer ---
barsik, _ = Cat.objects.get_or_create(
    name='Барсик', owner=viewer,
    defaults={'color': 'Gray', 'birth_year': 2020},
)

# --- Лайки и избранное (viewer лайкает котиков demo) ---
Like.objects.get_or_create(user=viewer, cat=marta)
Like.objects.get_or_create(user=viewer, cat=simba)
Like.objects.get_or_create(user=demo, cat=barsik)
Favorite.objects.get_or_create(user=viewer, cat=marta)

# --- Достижение ---
achievement, _ = Achievement.objects.get_or_create(name='Путешественник')

# --- Публичное путешествие demo ---
travel_public, _ = Travel.objects.get_or_create(
    cat=marta, title='Летняя поездка',
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
    travel=travel_public, order=1,
    defaults={
        'city': 'Казань', 'country': 'Россия',
        'address': 'ул. Баумана, 1',
        'arrival_date': date(2026, 6, 1),
        'departure_date': date(2026, 6, 5),
        'notes': 'Отель разрешает проживание с животными.',
    },
)

TravelChecklistItem.objects.get_or_create(
    travel=travel_public, title='Получить ветеринарную справку',
    defaults={'is_done': False, 'due_date': date(2026, 5, 30)},
)

# --- Приватное путешествие viewer (чтобы demo не мог его трогать) ---
travel_private, _ = Travel.objects.get_or_create(
    cat=barsik, title='Дача с Барсиком',
    defaults={
        'destination': 'Подмосковье',
        'start_date': date(2026, 7, 10),
        'end_date': date(2026, 7, 20),
        'transport': 'машина',
        'status': 'planned',
        'is_public': False,
        'notes': 'Приватная поездка.',
    },
)

print('=' * 50)
print('Пользователи:')
print(f'  demo   / Demo1234!   (superuser, владелец Marta и Simba)')
print(f'  viewer / Viewer1234! (владелец Барсика)')
print(f'Котики: Marta (id={marta.id}), Simba (id={simba.id}), Барсик (id={barsik.id})')
print(f'Путешествия: публичное "{travel_public.title}" (id={travel_public.id}, demo),')
print(f'             приватное "{travel_private.title}" (id={travel_private.id}, viewer)')
print('=' * 50)
EOF

echo ""
echo "Контейнер запущен."
echo "API:        http://127.0.0.1:8001/"
echo "Админка:    http://127.0.0.1:8001/admin/"
echo ""
echo "Демо-вход:"
echo "  demo   / Demo1234!   (главный пользователь)"
echo "  viewer / Viewer1234! (для демонстрации запретов)"
echo ""
echo "Логи:    docker compose logs -f web"
echo "Стоп:    ./stop.sh"
