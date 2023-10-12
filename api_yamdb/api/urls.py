from django.urls import include, path
from rest_framework import routers

from .views import (SignUpViewSet, TokenViewSet, UserViewSet)

app_name = 'api'

router = routers.DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('auth/signup', SignUpViewSet, basename='signup')
router.register('auth/token', TokenViewSet, basename='token')

urlpatterns = [
    path('v1/', include(router.urls)),
]
