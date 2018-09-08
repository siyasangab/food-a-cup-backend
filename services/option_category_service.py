from django.db.models import Q

from .base.service_base import ServiceBase
from .cache.option_categories_cache import OptionCategoriesCache
from domain.models import OptionCategory

class OptionCategoryService(ServiceBase):
    def __init__(self):
        self.cache = OptionCategoriesCache()
        super(OptionCategoryService, self).__init__(OptionCategory)

    def create(self, **kwargs):
        try:
            option_category = OptionCategory()
            option_category.heading = kwargs.get('heading')
            option_category.restaurant = kwargs.get('restaurant')
            option_category.save()
            return option_category.id
        except:
            return -99

    def get(self, id):
        try:
            option_category = OptionCategory.objects.get(pk = id)
            return option_category
        except OptionCategory.DoesNotExist:
            return None

    def get_by_restaurant(self, restaurant):
        cache_key = f'get_by_restaurant/?restaurant={restaurant}'

        option_categories = self.cache.get(cache_key, None)
        if option_categories != None:
            return option_categories

        q = Q()
        q &= Q(restaurant_id = restaurant)
        option_categories = list(OptionCategory.objects.prefetch_related('options').filter(q))

        self.cache.set(cache_key, option_categories)
        return option_categories

    def update(self, id, **kwargs):
        option_category = self.get(id)

        if option_category == None:
            return False

        option_category.heading = kwargs.get('heading')
        option_category.active = kwargs.get('active')
        option_category.save()

        return True

    def is_appuser_admin(self, appuser_id, id):
        cache_key = f'is_appuser_admin/?appuser_id={appuser_id}&id={id}'
        is_admin = self.cache.get(cache_key)

        if is_admin != None:
            return is_admin

        q = Q()
        q &= Q(id = id)
        q &= Q(restaurant__appuser_id = appuser_id)
        try:
            is_admin = OptionCategory.objects.select_related('restaurant').filter(q).exists()
        except Exception as e:
            print(e)
            is_admin = False
        
        self.cache.set(cache_key, is_admin)

        return is_admin
        