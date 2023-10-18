from django.urls import include, path
from rest_framework import routers

from api.views import (CommentViewSet,
                       CategoryViewSet,
                       GenreViewSet,
                       ReviewViewSet,
                       SignUpViewSet,
                       TitleViewSet,
                       TokenViewSet,
                       UserViewSet,
                       )


app_name = 'api'

router_v1 = routers.DefaultRouter()

router_v1.register(
    prefix='users',
    viewset=UserViewSet,
    basename='users')
router_v1.register(
    prefix='auth/signup',
    viewset=SignUpViewSet,
    basename='signup')
router_v1.register(
    prefix='auth/token',
    viewset=TokenViewSet,
    basename='token')
router_v1.register(
    prefix='categories',
    viewset=CategoryViewSet,
    basename='categories')
router_v1.register(
    prefix='genres',
    viewset=GenreViewSet,
    basename='genres')
router_v1.register(
    prefix='titles',
    viewset=TitleViewSet,
    basename='titles')
router_v1.register(
    prefix=r'titles/(?P<title_id>\d+)/reviews',
    viewset=ReviewViewSet,
    basename='reviews')
router_v1.register(
    prefix=r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    viewset=CommentViewSet,
    basename='comments')


urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
