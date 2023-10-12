from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from reviews.models import Comments, Reviews, User


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
        if username in 'me':
            raise serializers.ValidationError(
                'Запрещено использовать me в качестве имени пользователя'
            )
        return username


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор регистрации пользователя.
    """

    email = serializers.EmailField(
        max_length=254, required=True,
        validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ('email', 'username')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('email', 'username'),
                message="Логин и email должны быть уникальными"
            )
        ]

    def validate_username(self, username):
        if username == 'me':
            raise ValidationError(
                'Запрещено использовать me в качестве имени пользователя'
            )
        return username


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
        max_length=50, validators=[UnicodeUsernameValidator, ]
    )
    confirmation_code = serializers.CharField()

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class ReviewsSerializer(serializers.ModelSerializer):
    """Сериализатор отзывов"""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Reviews
        fields = '__all__'

    def validate_score(self, star):
        if not 1 <= star <= 10:
            raise ValidationError('Допустимое значение от 1 до 10')
        return star


class CommentsSerializer(serializers.ModelSerializer):
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
        model = Comments
        fields = '__all__'
