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
