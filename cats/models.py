from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint

CHOICES = (
    ('Gray', 'Серый'),
    ('Black', 'Чёрный'),
    ('White', 'Белый'),
    ('Ginger', 'Рыжий'),
    ('Mixed', 'Смешанный'),
)

User = get_user_model()


class Achievement(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Cat(models.Model):
    name = models.CharField(max_length=16)
    color = models.CharField(max_length=16, choices=CHOICES)
    birth_year = models.IntegerField()
    owner = models.ForeignKey(
        User, related_name='cats', on_delete=models.CASCADE)
    achievements = models.ManyToManyField(Achievement, through='AchievementCat')

    def __str__(self):
        return self.name


class AchievementCat(models.Model):
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.achievement} {self.cat}'


class Like(models.Model):
    user = models.ForeignKey(
        User, related_name='likes', on_delete=models.CASCADE
    )
    cat = models.ForeignKey(
        Cat, related_name='likes', on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        constraints = [
            UniqueConstraint(
                fields=('user', 'cat'),
                name='unique_like_per_user_cat',
            ),
        ]

    def __str__(self):
        return f'{self.user} likes {self.cat}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, related_name='favorites', on_delete=models.CASCADE
    )
    cat = models.ForeignKey(
        Cat, related_name='favorites', on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        constraints = [
            UniqueConstraint(
                fields=('user', 'cat'),
                name='unique_favorite_per_user_cat',
            ),
        ]

    def __str__(self):
        return f'{self.user} favorited {self.cat}'


class Travel(models.Model):
    PLANNED = 'planned'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

    STATUS_CHOICES = (
        (PLANNED, 'Запланировано'),
        (IN_PROGRESS, 'В пути'),
        (COMPLETED, 'Завершено'),
        (CANCELLED, 'Отменено'),
    )

    cat = models.ForeignKey(
        Cat, related_name='travels', on_delete=models.CASCADE
    )
    title = models.CharField(max_length=80)
    destination = models.CharField(max_length=120)
    start_date = models.DateField()
    end_date = models.DateField()
    transport = models.CharField(max_length=80, blank=True)
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default=PLANNED
    )
    is_public = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-start_date', 'id')

    def __str__(self):
        return f'{self.title}: {self.cat}'


class TravelStop(models.Model):
    travel = models.ForeignKey(
        Travel, related_name='stops', on_delete=models.CASCADE
    )
    order = models.PositiveSmallIntegerField()
    city = models.CharField(max_length=80)
    country = models.CharField(max_length=80)
    address = models.CharField(max_length=160, blank=True)
    arrival_date = models.DateField()
    departure_date = models.DateField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ('travel', 'order')
        constraints = [
            UniqueConstraint(
                fields=('travel', 'order'),
                name='unique_stop_order_per_travel',
            ),
        ]

    def __str__(self):
        return f'{self.order}. {self.city} ({self.travel})'


class TravelChecklistItem(models.Model):
    travel = models.ForeignKey(
        Travel, related_name='checklist', on_delete=models.CASCADE
    )
    title = models.CharField(max_length=120)
    is_done = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('is_done', 'due_date', 'id')
        constraints = [
            UniqueConstraint(
                fields=('travel', 'title'),
                name='unique_checklist_title_per_travel',
            ),
        ]

    def __str__(self):
        return f'{self.title}: {self.travel}'
