from .base.service_base import ServiceBase
from . import restaurants_service
from . import meal_service
from .cache.prepop_cache import PrepopCache
from domain.models import Restaurant

class PrepopService(ServiceBase):
    def __init__(self):
        print('Setting prepop data...')
        self.cache = PrepopCache()
        
        field_list = ('name', 'city', 'suburb')
        svc_ctx = restaurants_service.RestaurantsService()
        restaurants = list(svc_ctx.get_fields(field_list, ** {}).distinct())
        self.data = []

        for d in restaurants:
            self.__add_to_list__(d['name'].title(), self.data)
            self.__add_to_list__(d['city'].title(), self.data)
            self.__add_to_list__(d['suburb'].title(), self.data)

        meal_ctx = meal_service.MealService()

        meal_field_list = ('name',)

        meals = list(meal_ctx.get_fields(meal_field_list, ** {}).distinct())

        for m in meals:
            self.__add_to_list__(m['name'].title(), self.data)

        self.cache.set('prepop', self.data)

    def get_all(self):
        return self.data

    def search(self, query = ''):
        if not query:
            return []

        query = query.lower()

        ret = []

        for d in self.data:
            if query == d.lower() or query in d.lower():
                ret.append(d)

        return ret

    def __add_to_list__(self, item, lst):
        print(f'adding {item} to prepop data...')
        if item not in lst:
            lst.append(item)
