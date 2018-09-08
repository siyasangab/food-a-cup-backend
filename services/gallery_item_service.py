import cloudinary

from domain.models import GalleryItem
from .restaurants_service import RestaurantsService
from .appuser_service import AppUserService
from .cache.galleryitems_cache import GalleryItemsCache

class GalleryItemService():
    def __init__(self):
       self.cache = GalleryItemsCache()

    def create(self, **kwargs):

        user_id = kwargs.get('user_id', 0)

        if user_id == 0:
            return None
        appuser_id = AppUserService().get_by_user_id(user_id).id

        Restaurant = RestaurantsService().get_by_appuser_id(appuser_id)

        data = cloudinary.uploader.upload(kwargs['image'])

        thumbnail = cloudinary.CloudinaryImage(data['public_id']).build_url(width = 150, height = 100, crop = 'fill').replace('http', 'https')

        full_image = cloudinary.CloudinaryImage(data['public_id']).build_url(width = 1250, height = 980, crop = 'fill').replace('http', 'https')

        gallery_item = GalleryItem.objects.create(**{
                            'full_image': full_image,
                            'thumbnail': thumbnail,
                            'public_id': data['public_id'],
                            'Restaurant': Restaurant
                        })

        return gallery_item

    def get_by_Restaurant_id(self, Restaurant_id):
        gallery_items = self.cache.get(Restaurant_id)

        if gallery_items != None:
            return gallery_items

        gallery_items = list(GalleryItem.objects.filter(Restaurant_id = Restaurant_id))

        self.cache.set(Restaurant_id, gallery_items)

        return gallery_items