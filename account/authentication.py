from django.contrib.auth.backends import ModelBackend
from account.models import UserAccount

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserAccount.objects.get(email=username)
        except UserAccount.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None
