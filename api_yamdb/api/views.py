from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
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
    IsUserOnlyPermission,
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
        permission_classes=(IsUserOnlyPermission,)
    )
    def me_user(self, request):
        if request.method == 'GET':
            user = User.objects.get(username=request.user)
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        user = User.objects.get(username=request.user)
        serializer = RoleSerializer(user, data=request.data, partial=True)
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

        user_exists = User.objects.filter(username=username, email=email)
        if user_exists:
            user = User.objects.get(username=username)
            serializer = RegistrationSerializer(user, data=request.data)
        else:
            serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(username=username)
            code = user.confirmation_code
            send_mail(
                f'{user.username}, Вас приветствует команда YaMDb! ',
                f'Это Ваш уникальный код: {code} '
                f'Перейдите по адресу api/v1/auth/token/'
                f'для получения токена',
                'yamdb@yyamdb.ru',
                [email],
                fail_silently=False,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenViewSet(viewsets.ModelViewSet):
    """
    Отправляет и обновляет токен пользователю.
    """
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        serializer = UserTokenSerializer(data=request.data)
        if serializer.is_valid():
            username = request.data.get('username')
            confirmation_code = request.data.get('confirmation_code')
            user = get_object_or_404(User, username=username)
            if str(user.confirmation_code) == confirmation_code:
                refresh = RefreshToken.for_user(user)
                token = {'token': str(refresh.access_token)}
                return Response(token, status=status.HTTP_200_OK)
        return Response(
            'Проверьте confirmation_code', status=status.HTTP_400_BAD_REQUEST
        )


class CategoryViewSet(CreateListDeleteViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnlyPermission,]


class GenreViewSet(CreateListDeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnlyPermission,]


class TitleViewSet(viewsets.ModelViewSet):
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    permission_classes = [IsAdminOrReadOnlyPermission,]

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            raise MethodNotAllowed(self.request.method)
        if self.request.method in ['POST', 'PATCH']:
            return TitlePostPatchSerializer
        return TitleSerializer

    def get_queryset(self):
        genre_slug = self.request.query_params.get('genre')
        category_slug = self.request.query_params.get('category')
        year = self.request.query_params.get('year')
        name = self.request.query_params.get('name')
        if genre_slug:
            genre = get_object_or_404(Genre, slug=genre_slug)
            return genre.genre_titles.all()
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            return category.category_titles.all()
        if year:
            return Title.objects.filter(year=year)
        if name:
            return Title.objects.filter(name=name)
        else:
            return Title.objects.all()


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет на отзывы"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorModeratorAdminOrReadOnlyPermission,]
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ['text',]
    filter_fields = ['score',]
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
    permission_classes = [IsAuthorModeratorAdminOrReadOnlyPermission,]
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ['text',]
    filter_fields = ['author__username',]
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
