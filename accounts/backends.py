from django.contrib.auth.backends import ModelBackend

from .models import User


class UserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(number=username)
            except User.DoesNotExist:
                return None

        if user.check_password(password):
            return user

        return None
