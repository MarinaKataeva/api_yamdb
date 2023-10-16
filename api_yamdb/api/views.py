from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


from api.permissions import (
    IsAdminOnlyPermission,
    IsUserOnlyPermission,
    IsAdminOrReadOnlyPermission,
    IsAuthorModeratorAdminOrReadOnlyPermission
)
from .serializers import (
    CustomSerializer,
    UserSerializer,
    RegistrationSerializer,
    CustomUserTokenSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    TitlePostPatchSerializer
)
from .mixins import CreateListDeleteViewSet
from api.serializers import CommentsSerializer, ReviewsSerializer
from reviews.models import Reviews, Title, User, Category, Genre


class UserViewSet(viewsets.ModelViewSet):
    """
    Работает над всеми операциями с пользователями от лица админа.
    Позволяет обычному пользователю редактировать свой профиль.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOnlyPermission,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        methods=['get'],
        detail=False,
        url_path='me',
        permission_classes=(IsUserOnlyPermission,)
    )
    def get_my_profile(self, request):
        """
        Профиль текущего пользователя.
        """

        user = get_object_or_404(User, username=request.user)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(
        methods=['patch'],
        detail=False,
        url_path='me',
        permission_classes=(IsUserOnlyPermission,)
    )
    def update_my_profile(self, request):
        """
        Обновление профиля текущего пользователя.
        """

        user = get_object_or_404(User, username=request.user)
        serializer = CustomSerializer(user, data=request.data, partial=True)
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

    @action(
        methods=['post'],
        detail=False,
        url_path='signup',
        permission_classes=[permissions.AllowAny]
    )
    def create_user(self, request):
        """
        Регистрация пользователя.
        """
        user = self.perform_create(request)

        if user:
            self.send_confirmation_email(user)
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, request):
        """
        Проверяет, существует ли уже пользователь с таким именем
        пользователя и электронной почтой, и если да, то обновляет
        данные пользователя.
        """
        serializer = RegistrationSerializer(data=request.data)

        username = request.data.get('username')
        email = request.data.get('email')

        if User.objects.filter(username=username, email=email).exists():
            user = User.objects.get(username=username)
            serializer = RegistrationSerializer(user, data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return user

        return None

    def send_confirmation_email(self, user):
        """
        Отправляет письмо с подтверждением на указанную
        электронную почту пользователя.
        """
        code = user.confirmation_code
        send_mail(
            (f'{user.username}, Вас приветствует команда YaMDb!',
             f'Это Ваш уникальный код: {code} '
             f'Перейдите по адресу api/v1/auth/token/ для получения токена'),
            [user.email],
            fail_silently=False,
        )


class TokenViewSet(viewsets.ModelViewSet):
    """
    Отправляет и обновляет токен пользователю.
    """
    permission_classes = (permissions.AllowAny,)

    @action(detail=False, methods=['post'])
    def create_token(self, request):
        serializer = CustomUserTokenSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            confirmation_code = serializer.validated_data['confirmation_code']
            user = get_object_or_404(User, username=username)

            if str(user.confirmation_code) == confirmation_code:
                refresh = RefreshToken.for_user(user)
                token = {'token': str(refresh.access_token)}
                return Response(token, status=status.HTTP_200_OK)

        return Response({'detail': 'Неверные данные'},
                        status=status.HTTP_400_BAD_REQUEST)


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


class ReviewsViewSet(viewsets.ModelViewSet):
    """Вьюсет на отзывы"""
    serializer_class = ReviewsSerializer
    permission_classes = [IsAuthorModeratorAdminOrReadOnlyPermission,]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentsViewSet(viewsets.ModelViewSet):
    """Вьюсет на комментарии"""
    serializer_class = CommentsSerializer
    permission_classes = [IsAuthorModeratorAdminOrReadOnlyPermission,]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        review = get_object_or_404(
            Reviews,
            id=self.kwargs.get('review_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Reviews,
            id=self.kwargs.get('review_id')
        )
        serializer.save(author=self.request.user, review=review)
