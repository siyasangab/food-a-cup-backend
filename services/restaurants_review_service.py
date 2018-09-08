from django.db.models import Q

from .base.service_base import ServiceBase
from .pagination_service import PaginationService, Pager
from domain.models import RestaurantReview

class RestaurantsReviewService(ServiceBase):
    def __init__(self):
        super(RestaurantsReviewService, self).__init__(RestaurantReview)


    def create(self, **kwargs):
        restaurant_review = RestaurantReview(**kwargs)
        restaurant_review.save()
        return restaurant_review


    def get(self, slug, page_number, page_size):
        q = Q()
        q &= Q(restaurant__slug = slug)

        pager = Pager(RestaurantReview.objects.select_related('rated_by').all(), page_number, page_size)
        paged = PaginationService().paginate(pager, q)

        return paged