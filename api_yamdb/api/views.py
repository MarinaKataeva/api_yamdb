from django.db.models import Avg
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django_filters import rest_framework
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.mixins import CreateListDeleteViewSet
from api.permissions import (
    IsAdminOnlyPermission,
    IsAdminOrReadOnlyPermission,
    IsAuthorModeratorAdminOrReadOnlyPermission
)
from api.serializers import (RoleSerializer, UserSerializer,
                             RegistrationSerializer, UserTokenSerializer,
                             CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             TitlePostPatchSerializer, TitleSerializer,
                             )
from reviews.models import Category, Comment, Genre, Review, Title, User


class UserViewSet(viewsets.ModelViewSet):
    """
    Работает над всеми операциями с пользователями от лица админа.
    Позволяет обычному пользователю редактировать свой профиль.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (IsAdminOnlyPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        methods=['get', 'patch'],
        detail=False,
        url_path='me',
        permission_classes=[permissions.IsAuthenticated])
    def me_user(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

        serializer = RoleSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignUpViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Осуществляет регистрацию пользователей.
    Отправляет код на электронную почту пользователя
    как при регистрации, так и при повторном валидном обращении.
    """
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        username = request.data.get('username')
        email = request.data.get('email')

        user_exists = User.objects.filter(
            username=username, email=email).exists()
        if user_exists:
            user = User.objects.get(username=username)
            serializer = RegistrationSerializer(user, data=request.data)
        else:
            serializer = RegistrationSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        code = user.confirmation_code
        send_mail(
            f'{user.username}, Вас приветствует команда YaMDb! ',
            f'Это Ваш уникальный код: {code} '
            f'Перейдите по адресу api/v1/auth/token/'
            f'для получения токена',
            settings.DEFAULT_EMAIL,
            [email],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenViewSet(viewsets.ModelViewSet):
    """
    Отправляет и обновляет токен пользователю.
    """
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        serializer = UserTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)
        confirmation_code = default_token_generator.make_token(user)
        if str(user.confirmation_code) == confirmation_code:
            refresh = RefreshToken.for_user(user)
            token = {'token': str(refresh.access_token)}
            return Response(token, status=status.HTTP_200_OK)
        return Response(
            'Проверьте confirmation_code', status=status.HTTP_400_BAD_REQUEST
        )


class CategoryViewSet(CreateListDeleteViewSet):
    """ Вьюсет категоргии произведения """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnlyPermission, ]


class GenreViewSet(CreateListDeleteViewSet):
    """ Вьюсет жанра произведения """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnlyPermission, ]


class TitleFilter(rest_framework.FilterSet):
    """ Фильтрсет для фильтрации по связанным моделям категории и жанра"""
    category = rest_framework.CharFilter(field_name='category__slug')
    genre = rest_framework.CharFilter(field_name='genre__slug')

    class Meta:
        model = Title
        fields = ['year', 'name', 'category', 'genre']


class TitleViewSet(viewsets.ModelViewSet):
    """ Вьюсет произведения """
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = [IsAdminOrReadOnlyPermission, ]
    pagination_class = LimitOffsetPagination
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            raise MethodNotAllowed(self.request.method)
        if self.request.method in ['POST', 'PATCH']:
            return TitlePostPatchSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет на отзывы"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorModeratorAdminOrReadOnlyPermission, ]
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ['text', ]
    filter_fields = ['score', ]
    lookup_field = 'pk'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return Review.objects.select_related('title').all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет на комментарии"""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorModeratorAdminOrReadOnlyPermission, ]
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ['text', ]
    filter_fields = ['author__username', ]
    lookup_field = 'pk'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_review(self):
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, id=review_id)

    def get_queryset(self):
        review = self.get_review()
        return Comment.objects.filter(review=review).select_related('author')

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)

        return Response(
            'Проверьте confirmation_code', status=status.HTTP_400_BAD_REQUEST
        )
