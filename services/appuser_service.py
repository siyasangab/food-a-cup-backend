from django.contrib.auth.models import User
from django.conf import settings

from domain.models import AppUser
from services.cache import app_users_cache
from .user_service import UserService
from .base.service_base import ServiceBase

class AppUserService(ServiceBase):
    def __init__(self, **kwargs):
        self.cache = app_users_cache.AppUsersCache()
        super(AppUserService, self).__init__(AppUser)
    
    def create(self, **kwargs):
        try:
            app_user = AppUser.objects.create(**kwargs)
            return app_user
        except Exception as e:
            raise Exception(e)

    def get_by_user_id(self, user_id):
        rint(f'Fetching appuser for user id {user_id}')
        cached = self.cache.get(user_id)

        if cached != None:
            return cached.get('appuser', None), cached.get('restaurants', None)

        try:
            app_user = AppUser.objects.prefetch_related('user').get(user_id = user_id)
            self.cache.set(user_id, app_user)
            return app_user

        except AppUser.DoesNotExist:
            print(f'An error occurred while getting appuser for user id {user_id}')
            return None

    def get_appuser_id_by_user_id(self, user_id):
        key = f'get_appuser_id_by_user_id/?user_id={user_id}'

        appuser_id = self.cache.get(key, None)

        if appuser_id != None:
            return appuser_id

        field_list = ('id',)
        result = self.get_fields(field_list, **{
                     'user_id': user_id
                 })

        appuser_id = result[0]['id'] if result else None
        self.cache.set(key, appuser_id, settings.FIFTEEN_MINUTES)

        return appuser_id

    def update(self, user_id, **kwargs):
        appuser = None
        try:
            appuser = self.get_by_user_id(user_id)
        except AppUser.DoesNotExist:
            return False

        appuser.city = kwargs.get('city')
        appuser.nickname = kwargs.get('nickname')

        try:
            appuser.save()
        except Exception as e:
            print(e)

        self.cache.set(user_id, appuser)

        return True


