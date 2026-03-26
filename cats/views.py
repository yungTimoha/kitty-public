from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Achievement, Cat, Favorite, Like, User

from .permissions import IsOwnerOrReadOnly
from .serializers import (
    AchievementSerializer,
    CatSerializer,
    FavoriteSerializer,
    LikeSerializer,
    UserSerializer,
)


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        queryset = Cat.objects.annotate(likes_count=Count('likes'))
        color = self.request.query_params.get('color')
        owner = self.request.query_params.get('owner')
        search = self.request.query_params.get('search')

        if color:
            queryset = queryset.filter(color=color)
        if owner:
            queryset = queryset.filter(owner_id=owner)
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset.order_by('id')

    @action(detail=True, methods=('post',))
    def like(self, request, pk=None):
        cat = self.get_object()
        serializer = LikeSerializer(
            data={'cat_id': cat.id},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=('delete',))
    def unlike(self, request, pk=None):
        cat = self.get_object()
        deleted, _ = Like.objects.filter(user=request.user, cat=cat).delete()
        if not deleted:
            return Response(
                {'detail': 'Лайк для этого котика не найден.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post',))
    def favorite(self, request, pk=None):
        cat = self.get_object()
        serializer = FavoriteSerializer(
            data={'cat_id': cat.id},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=('delete',))
    def unfavorite(self, request, pk=None):
        cat = self.get_object()
        deleted, _ = Favorite.objects.filter(
            user=request.user, cat=cat
        ).delete()
        if not deleted:
            return Response(
                {'detail': 'Котик не найден в избранном.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('get',))
    def my_likes(self, request):
        queryset = self.filter_queryset(
            self.get_queryset().filter(likes__user=request.user)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=('get',))
    def my_favorites(self, request):
        queryset = self.filter_queryset(
            self.get_queryset().filter(favorites__user=request.user)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=('get',))
    def top(self, request):
        queryset = self.filter_queryset(
            self.get_queryset().order_by('-likes_count', 'id')
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer


class LikeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LikeSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Like.objects.filter(user=self.request.user).select_related('cat')


class FavoriteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related(
            'cat'
        )
