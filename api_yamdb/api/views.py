from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from api.permissions import (IsAdminOnlyPermission, IsUserOnlyPermission)
from api.serializers import (RoleSerializer, UserSerializer,
                             RegistrationSerializer, UserTokenSerializer)
from reviews.models import User


class UserViewSet(viewsets.ModelViewSet):
    """
    Работает над всеми операциями с пользователями от лица админа.
    Позволяет обычному пользователю редактировать свой профиль.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (IsAdminOnlyPermission,)
    pagination_class = PageNumberPagination
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
