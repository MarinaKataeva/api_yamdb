from django.contrib.auth.validators import UnicodeUsernameValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import User, Category, Genre, Title, GenreTitle


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.
    """

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )

    def validate_username(self, username):
        """
        Проверка, что username не равен "me".
        """
        if username in 'me':
            raise serializers.ValidationError(
                'Запрещено использовать me в качестве имени пользователя'
            )
        return username


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор регистрации пользователя.
    """

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate(self, data):
        if data.get('username') == 'me':
            raise serializers.ValidationError(
                'Запрещено использовать me в качестве имени'
            )
        if User.objects.filter(username=data.get('username')):
            raise serializers.ValidationError(
                'Пользователь с таким именем уже существует'
            )
        if User.objects.filter(email=data.get('email')):
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует'
            )
        return data


class CustomSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)


class CustomUserTokenSerializer(serializers.ModelSerializer):
    """
    Сериализатор для токена.
    """
    username = serializers.CharField(
        max_length=50, validators=[UnicodeUsernameValidator, ]
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
    """ Сериализатор для произведения"""
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )
        model = Title

    def validate(self, data):
        print('Start data validation...')
        print(f'Data = {data}')
        if 'name' not in data:
            raise serializers.ValidationError(
                'Не указано наименование произведения'
            )
        if 'year' not in data:
            raise serializers.ValidationError(
                'Не указан год выпуска произведения'
            )
        if 'genre' not in data:
            raise serializers.ValidationError(
                'Не указан жанр произведения'
            )
        if 'category' not in data:
            raise serializers.ValidationError(
                'Не указана категория произведения'
            )
        return data

    def create(self, validated_data):
        # name year genre category
        print(f'Validated data = f{validated_data}')
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre in genres:
            current_genre = get_object_or_404(Genre, name=genre)
            GenreTitle.objects.create(
                genre=current_genre, title=title)
        return title
