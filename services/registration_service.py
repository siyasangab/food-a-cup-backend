from django.db import transaction
from django.contrib.auth.models import User, Group

from domain.models import AppUser
from services.appuser_service import AppUserService
from services.user_service import UserService
from utils.hash import hash_string

class RegistrationService():
    def __init__(self):
        pass

    def create(self, **kwargs):
        with transaction.atomic():
            cellphone = kwargs.get('cellphone')
            user = UserService().create(**kwargs.get('user'))
            app_user = AppUserService().create(**{ 
                'user_id': user.id, 
                'cellphone':  cellphone,
                'accepted_terms': True
            })

            grp = Group.objects.get(name = 'Customer')
            grp.user_set.add(user)
            return app_user



