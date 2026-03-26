from rest_framework import routers

from django.contrib import admin
from django.urls import include, path

from cats.views import (
    AchievementViewSet,
    CatViewSet,
    FavoriteViewSet,
    LikeViewSet,
    UserViewSet,
)


router = routers.DefaultRouter()
router.register('cats', CatViewSet)
router.register('users', UserViewSet)
router.register('achievements', AchievementViewSet)
router.register('likes', LikeViewSet, basename='likes')
router.register('favorites', FavoriteViewSet, basename='favorites')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
