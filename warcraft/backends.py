from django.conf import settings
from django.contrib.auth.models import check_password
from warcraft.models import User

class UserAuthBackend(object):
    """
    A custom authentication backend. Allows users to log in using their email address.
    """

    def authenticate(self, userName=None, password=None):
        """
        Authentication method
        """
        try:
            user = User.objects.get(userName=userName)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            if user.is_active:
                return user
            return None
        except User.DoesNotExist:
            return None