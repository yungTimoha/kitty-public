from rest_framework import routers

from django.contrib import admin
from django.urls import include, path

from cats.views import (
    AchievementViewSet,
    CatViewSet,
    FavoriteViewSet,
    LikeViewSet,
    TravelChecklistItemViewSet,
    TravelStopViewSet,
    TravelViewSet,
    UserViewSet,
)


router = routers.DefaultRouter()
router.register('cats', CatViewSet)
router.register('users', UserViewSet)
router.register('achievements', AchievementViewSet)
router.register('likes', LikeViewSet, basename='likes')
router.register('favorites', FavoriteViewSet, basename='favorites')
router.register('travels', TravelViewSet, basename='travels')
router.register('travel-stops', TravelStopViewSet, basename='travel-stops')
router.register(
    'travel-checklist',
    TravelChecklistItemViewSet,
    basename='travel-checklist',
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
