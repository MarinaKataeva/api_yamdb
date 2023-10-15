from django.urls import include, path
from rest_framework import routers

from .views import (
    SignUpViewSet,
    TokenViewSet,
    UserViewSet,
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet
)

app_name = 'api'

router_v1 = routers.DefaultRouter()

router_v1.register('users', UserViewSet, basename='users')
router_v1.register('auth/signup', SignUpViewSet, basename='sign-up')
router_v1.register('auth/token', TokenViewSet, basename='token')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
