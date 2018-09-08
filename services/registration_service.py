from django.db import transaction
from django.contrib.auth.models import User, Group

from domain.models import AppUser
from services.appuser_service import AppUserService
from services.restaurants_service import RestaurantsService
from services.user_service import UserService

class RegistrationService():
    def __init__(self):
        pass

    def create(self, **kwargs):
        with transaction.atomic():
            cellphone = kwargs.get('cellphone')
            city = kwargs.get('city')
            nickname = kwargs.get('nickname')
            
            del kwargs['cellphone']
            del kwargs['city']
            del kwargs['nickname']

            user = UserService().create(**kwargs)

            app_user = AppUserService().create(**{ 
                'user': user, 
                'cellphone_number':  cellphone,
                'city': city,
                'nickname': nickname
            })

            grp = Group.objects.get(name = 'Users')
            grp.user_set.add(user)
            return app_user



