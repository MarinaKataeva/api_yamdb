from django.urls import include, path
from rest_framework import routers

from .views import (CommentsViewSet, ReviewsViewSet,
                    SignUpViewSet, TokenViewSet, UserViewSet)

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
    prefix=r'titles/(?P<title_id>\d+)/reviews',
    viewset=ReviewsViewSet,
    basename='reviews')
router_v1.register(
    prefix=r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    viewset=CommentsViewSet,
    basename='comments')


urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
