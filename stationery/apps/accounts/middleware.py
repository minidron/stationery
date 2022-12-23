from django.contrib import auth
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.utils.functional import SimpleLazyObject

from .models import AnonymousUser


def get_user(request):
    """
    Подменяем модель `AnonymousUser`.
    """
    if not hasattr(request, '_cached_user'):
        user = auth.get_user(request)
        if user.is_anonymous:
            user = AnonymousUser()
        request._cached_user = user
    return request._cached_user


class AuthMiddleware(AuthenticationMiddleware):
    """
    Подменяем модель `AnonymousUser`.
    """

    def process_request(self, request):
        assert hasattr(request, 'session')
        request.user = SimpleLazyObject(lambda: get_user(request))
