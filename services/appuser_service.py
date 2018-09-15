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
            logger.exception('Could not create appuser')


    def get(self, appuser_id: int = 0, email: str = '', by = 'id'):
        try:
            if by == 'id':
                if appuser_id == 0:
                    raise ValueError('Appuser id is required when searching appuser by id')
                appuser = AppUser.objects.get(pk = appuser_id)
            elif by == 'email':
                if not email:
                    raise ValueError('Appuser email is required when searching appuser by email')
                appuser = AppUser.objects.select_related('user').get(user__email = email)
            return appuser
        except Exception as e:
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

    def update(self, appuser_id, **kwargs):
        appuser = self.get(appuser_id)
        if not appuser:
            return False

        appuser.city = kwargs.get('city')
        appuser.nickname = kwargs.get('nickname')

        try:
            appuser.save()
        except Exception as e:
            return False

        self.cache.set(appuser_id, appuser)

        return True


