from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from api.permissions import (IsAdminOnlyPermission, IsUserOnlyPermission)
from api.serializers import (CustomSerializer, UserSerializer,
                             RegistrationSerializer, CustomUserTokenSerializer)
from reviews.models import User


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
