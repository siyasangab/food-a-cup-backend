from django.contrib.auth.models import User, Group

class UserService():
    def __init__(self):
        pass

    def create(self, **kwargs):
        user = User(**kwargs)
        user.email = user.username
        user.set_password(kwargs.get('password'))
        user.save()
        return user

