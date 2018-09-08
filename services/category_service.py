from domain.models import Category
from .base.service_base import ServiceBase
from .cache.categories_cache import CategoriesCache

class CategoryService(ServiceBase):
    def __init__(self):
        self.cache = CategoriesCache()
        super(CategoryService, self).__init__(Category)

    def get(self, id):
        try:
            category = Category.objects.get(pk = id)
            return category
        except Category.DoesNotExist:
            return None

    def update(self, id, **kwargs):
        category = self.get(id)
        if category == None:
            return False

        category.name = kwargs.get('name')
        category.save()

        return True

    def is_appuser_admin(self, appuser_id, category_id):
        cache_key = f'is_appuser_admin?appuser_id={appuser_id}&category_id={category_id}'
        result = self.cache.get(cache_key)

        if result != None:
            return result

        lst = list(Category.objects.select_related('restaurant').filter(restaurant__appuser_id = appuser_id).values('id'))
        result = int(category_id) in [item['id'] for item in lst]

        self.cache.set(cache_key, result)

        return result
