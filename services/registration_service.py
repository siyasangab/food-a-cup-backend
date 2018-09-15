from django.db import transaction
from django.contrib.auth.models import User, Group

from domain.models import AppUser
from services.appuser_service import AppUserService
from services.user_service import UserService
from utils.hash import hash_string
from services.notification_service import NotificationService

class RegistrationService():
    def __init__(self):
        self._notification_service = NotificationService()
        self._appuser_service = AppUserService()
        self._user_service = UserService()

    def create(self, **kwargs):
        with transaction.atomic():
            cellphone = kwargs.get('cellphone')
            user = self._user_service.create(**kwargs.get('user'))
            app_user = self._appuser_service.create(**{ 
                'user_id': user.id, 
                'cellphone':  cellphone,
                'accepted_terms': True
            })

            grp = Group.objects.get(name = 'Customer')
            grp.user_set.add(user)

            verification_code = 1234

            self._notification_service.send_sms(
                to = cellphone,
                msg = f'Your FoodACup verification code: {verification_code}'
            )

            return app_user
