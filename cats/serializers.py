from rest_framework import serializers

import datetime as dt

from .models import (
    CHOICES,
    Achievement,
    AchievementCat,
    Cat,
    Favorite,
    Like,
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
