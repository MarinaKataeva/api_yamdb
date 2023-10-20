from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import (Category,
                            Comment,
                            Genre,
                            GenreTitle,
                            Review,
                            Title,
                            User)

MIN_SCORE = 1
MAX_SCORE = 10


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.
    """

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор регистрации пользователя.
    """

    email = serializers.EmailField(
        max_length=254, required=True,
        validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ('username', 'email')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }


class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)


class UserTokenSerializer(serializers.ModelSerializer):
    """
    Сериализатор для токена.
    """
    username = serializers.CharField(
        max_length=50
    )
    confirmation_code = serializers.CharField()

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class CategorySerializer(serializers.ModelSerializer):
    """ Сериализатор для категории произведения"""
    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class GenreSerializer(serializers.ModelSerializer):
    """ Сериализатор для жанра произведения"""
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class TitleSerializer(serializers.ModelSerializer):
    """ Сериализатор для чтения произведения"""
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.FloatField()

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )


class TitlePostPatchSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category'
        )

    def validate(self, data):
        """ Приводим данные к нужному формату для записи """
        category = get_object_or_404(
            Category,
            slug=self.initial_data['category']
        )
        data['category'] = category
        initial_genres = self.initial_data.getlist('genre')
        genre = []
        for initial_genre in initial_genres:
            genre.append(get_object_or_404(Genre, slug=initial_genre))
        data['genre'] = genre
        return data

    def create(self, validated_data):
        """ Создает запись в БД о произведении"""
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre in genres:
            GenreTitle.objects.create(
                genre=genre, title=title)
        return title


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзывов"""
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    score = serializers.IntegerField(
        min_value=MIN_SCORE,
        max_value=MAX_SCORE)

    class Meta:
        model = Review
        fields = '__all__'

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        if request.method == 'POST':
            existing_review = Review.objects.filter(
                title=title_id,
                author=author).first()
            if existing_review:
                raise serializers.ValidationError(
                    'Можно оставить только один отзыв!')
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев"""
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = '__all__'
