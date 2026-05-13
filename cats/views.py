from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    Achievement,
    Cat,
    Favorite,
    Like,
    Travel,
    TravelChecklistItem,
    TravelStop,
    User,
)

from .permissions import (
    IsOwnerOrReadOnly,
    IsTravelOwner,
    IsTravelOwnerOrPublicReadOnly,
)
from .serializers import (
    AchievementSerializer,
    CatSerializer,
    FavoriteSerializer,
    LikeSerializer,
    TravelChecklistItemSerializer,
    TravelSerializer,
    TravelStopSerializer,
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

    @action(detail=True, methods=('post',), permission_classes=(IsAuthenticated,))
    def like(self, request, pk=None):
        cat = self.get_object()
        serializer = LikeSerializer(
            data={'cat_id': cat.id},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=('delete',), permission_classes=(IsAuthenticated,))
    def unlike(self, request, pk=None):
        cat = self.get_object()
        deleted, _ = Like.objects.filter(user=request.user, cat=cat).delete()
        if not deleted:
            return Response(
                {'detail': 'Лайк для этого котика не найден.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post',), permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        cat = self.get_object()
        serializer = FavoriteSerializer(
            data={'cat_id': cat.id},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=('delete',), permission_classes=(IsAuthenticated,))
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


class TravelViewSet(viewsets.ModelViewSet):
    serializer_class = TravelSerializer
    permission_classes = (IsAuthenticated, IsTravelOwnerOrPublicReadOnly)

    def get_queryset(self):
        queryset = Travel.objects.select_related('cat', 'cat__owner').prefetch_related(
            'stops'
        )
        queryset = queryset.filter(
            Q(cat__owner=self.request.user) | Q(is_public=True)
        )

        cat = self.request.query_params.get('cat')
        status_param = self.request.query_params.get('status')
        destination = self.request.query_params.get('destination')
        is_public = self.request.query_params.get('is_public')

        if cat:
            queryset = queryset.filter(cat_id=cat)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if destination:
            queryset = queryset.filter(destination__icontains=destination)
        if is_public in ('true', 'false'):
            queryset = queryset.filter(is_public=is_public == 'true')

        return queryset

    @action(detail=False, methods=('get',))
    def my(self, request):
        queryset = self.filter_queryset(
            self.get_queryset().filter(cat__owner=request.user)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TravelStopViewSet(viewsets.ModelViewSet):
    serializer_class = TravelStopSerializer
    permission_classes = (IsAuthenticated, IsTravelOwnerOrPublicReadOnly)

    def get_queryset(self):
        queryset = TravelStop.objects.select_related(
            'travel', 'travel__cat', 'travel__cat__owner'
        )
        queryset = queryset.filter(
            Q(travel__cat__owner=self.request.user) | Q(travel__is_public=True)
        )
        travel = self.request.query_params.get('travel')
        if travel:
            queryset = queryset.filter(travel_id=travel)
        return queryset


class TravelChecklistItemViewSet(viewsets.ModelViewSet):
    serializer_class = TravelChecklistItemSerializer
    permission_classes = (IsAuthenticated, IsTravelOwner)

    def get_queryset(self):
        queryset = TravelChecklistItem.objects.select_related(
            'travel', 'travel__cat', 'travel__cat__owner'
        )
        queryset = queryset.filter(travel__cat__owner=self.request.user)
        travel = self.request.query_params.get('travel')
        is_done = self.request.query_params.get('is_done')
        if travel:
            queryset = queryset.filter(travel_id=travel)
        if is_done in ('true', 'false'):
            queryset = queryset.filter(is_done=is_done == 'true')
        return queryset
