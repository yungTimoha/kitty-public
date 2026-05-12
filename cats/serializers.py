from rest_framework import serializers

import datetime as dt

from .models import (
    CHOICES,
    Achievement,
    AchievementCat,
    Cat,
    Favorite,
    Like,
    Travel,
    TravelChecklistItem,
    TravelStop,
    User,
)


class UserSerializer(serializers.ModelSerializer):
    cats = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'cats')
        ref_name = 'ReadOnlyUsers'


class AchievementSerializer(serializers.ModelSerializer):
    achievement_name = serializers.CharField(source='name')

    class Meta:
        model = Achievement
        fields = ('id', 'achievement_name')


class CatSerializer(serializers.ModelSerializer):
    achievements = AchievementSerializer(many=True, required=False)
    color = serializers.ChoiceField(choices=CHOICES)
    age = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Cat
        fields = (
            'id',
            'name',
            'color',
            'birth_year',
            'achievements',
            'owner',
            'age',
            'likes_count',
            'is_liked',
            'is_favorited',
        )
        read_only_fields = ('owner',)

    def get_age(self, obj):
        return dt.datetime.now().year - obj.birth_year

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.likes.filter(user=request.user).exists()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def create(self, validated_data):
        if 'achievements' not in self.initial_data:
            cat = Cat.objects.create(
                owner=self.context['request'].user,
                **validated_data,
            )
            return cat
        else:
            achievements = validated_data.pop('achievements')
            cat = Cat.objects.create(
                owner=self.context['request'].user,
                **validated_data,
            )
            for achievement in achievements:
                current_achievement, status = Achievement.objects.get_or_create(
                    **achievement)
                AchievementCat.objects.create(
                    achievement=current_achievement, cat=cat)
            return cat


class UserCatRelationSerializer(serializers.ModelSerializer):
    cat_id = serializers.PrimaryKeyRelatedField(
        source='cat',
        queryset=Cat.objects.all(),
    )
    cat = CatSerializer(read_only=True)

    class Meta:
        fields = ('id', 'cat_id', 'cat', 'created_at')
        read_only_fields = ('id', 'cat', 'created_at')

    def validate(self, attrs):
        model = self.Meta.model
        user = self.context['request'].user
        cat = attrs['cat']
        if model.objects.filter(user=user, cat=cat).exists():
            raise serializers.ValidationError(
                {'detail': self.Meta.duplicate_error}
            )
        return attrs

    def create(self, validated_data):
        return self.Meta.model.objects.create(
            user=self.context['request'].user,
            **validated_data,
        )


class LikeSerializer(UserCatRelationSerializer):
    class Meta(UserCatRelationSerializer.Meta):
        model = Like
        duplicate_error = 'Вы уже лайкнули этого котика.'


class FavoriteSerializer(UserCatRelationSerializer):
    class Meta(UserCatRelationSerializer.Meta):
        model = Favorite
        duplicate_error = 'Этот котик уже в избранном.'


class TravelStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelStop
        fields = (
            'id',
            'travel',
            'order',
            'city',
            'country',
            'address',
            'arrival_date',
            'departure_date',
            'notes',
        )

    def validate_travel(self, travel):
        request = self.context['request']
        if travel.cat.owner != request.user:
            raise serializers.ValidationError(
                'Можно добавлять точки только в свои путешествия.'
            )
        return travel

    def validate(self, attrs):
        instance = self.instance
        arrival_date = attrs.get(
            'arrival_date',
            instance.arrival_date if instance else None,
        )
        departure_date = attrs.get(
            'departure_date',
            instance.departure_date if instance else None,
        )
        travel = attrs.get('travel', instance.travel if instance else None)

        if arrival_date and departure_date and departure_date < arrival_date:
            raise serializers.ValidationError(
                {'departure_date': 'Дата выезда не может быть раньше заезда.'}
            )
        if travel and arrival_date and arrival_date < travel.start_date:
            raise serializers.ValidationError(
                {'arrival_date': 'Точка маршрута не может начинаться раньше путешествия.'}
            )
        if travel and departure_date and departure_date > travel.end_date:
            raise serializers.ValidationError(
                {'departure_date': 'Точка маршрута не может заканчиваться позже путешествия.'}
            )
        if travel and 'order' in attrs:
            duplicate = TravelStop.objects.filter(
                travel=travel,
                order=attrs['order'],
            )
            if instance:
                duplicate = duplicate.exclude(pk=instance.pk)
            if duplicate.exists():
                raise serializers.ValidationError(
                    {'order': 'В путешествии уже есть точка с таким порядковым номером.'}
                )
        return attrs


class TravelChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelChecklistItem
        fields = (
            'id',
            'travel',
            'title',
            'is_done',
            'due_date',
            'created_at',
        )
        read_only_fields = ('created_at',)

    def validate_travel(self, travel):
        request = self.context['request']
        if travel.cat.owner != request.user:
            raise serializers.ValidationError(
                'Можно добавлять задачи только в свои путешествия.'
            )
        return travel

    def validate(self, attrs):
        instance = self.instance
        due_date = attrs.get('due_date', instance.due_date if instance else None)
        travel = attrs.get('travel', instance.travel if instance else None)
        if due_date and travel and due_date > travel.start_date:
            raise serializers.ValidationError(
                {'due_date': 'Срок подготовки должен быть не позже даты начала путешествия.'}
            )
        if travel and 'title' in attrs:
            duplicate = TravelChecklistItem.objects.filter(
                travel=travel,
                title=attrs['title'],
            )
            if instance:
                duplicate = duplicate.exclude(pk=instance.pk)
            if duplicate.exists():
                raise serializers.ValidationError(
                    {'title': 'Такая задача уже есть в чек-листе путешествия.'}
                )
        return attrs


class TravelSerializer(serializers.ModelSerializer):
    cat_name = serializers.CharField(source='cat.name', read_only=True)
    owner = serializers.IntegerField(source='cat.owner_id', read_only=True)
    stops = TravelStopSerializer(many=True, read_only=True)

    class Meta:
        model = Travel
        fields = (
            'id',
            'cat',
            'cat_name',
            'owner',
            'title',
            'destination',
            'start_date',
            'end_date',
            'transport',
            'status',
            'is_public',
            'notes',
            'stops',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')

    def validate_cat(self, cat):
        request = self.context['request']
        if cat.owner != request.user:
            raise serializers.ValidationError(
                'Можно создавать путешествия только для своих котиков.'
            )
        return cat

    def validate(self, attrs):
        instance = self.instance
        start_date = attrs.get(
            'start_date',
            instance.start_date if instance else None,
        )
        end_date = attrs.get('end_date', instance.end_date if instance else None)

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                {'end_date': 'Дата окончания не может быть раньше даты начала.'}
            )
        if instance and start_date:
            invalid_stop = instance.stops.filter(arrival_date__lt=start_date)
            if invalid_stop.exists():
                raise serializers.ValidationError(
                    {'start_date': 'Новая дата начала конфликтует с точками маршрута.'}
                )
        if instance and end_date:
            invalid_stop = instance.stops.filter(departure_date__gt=end_date)
            if invalid_stop.exists():
                raise serializers.ValidationError(
                    {'end_date': 'Новая дата окончания конфликтует с точками маршрута.'}
                )
        return attrs
