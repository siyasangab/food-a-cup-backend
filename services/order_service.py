import datetime

from domain.models import Order, OrderLineItem
from domain.constants import ORDER_ACCEPTED_STATUS, CANNOT_CHANGE_ORDER_MSG, ORDER_CANCELLED_STATUS, ORDER_CANCELLED_BY_CUSTOMER
from .base.service_base import ServiceBase
from .menu_service import MenuService
from django.db.transaction import atomic
from django.db.models import Q

class OrderService(ServiceBase):
    def __init__(self):
        super(OrderService, self).__init__(Order)
        self._menu = MenuService()

    def validate(self, **kwargs):
        menu_items = self._menu.get_menu_items_by_restaurant(kwargs.get('restaurant').id)
        if not menu_items:
            return False

        is_valid = set(detail['menu_item'].id for detail in kwargs.get('line_items')).issubset(menu_item.id for menu_item in menu_items)

        return is_valid
        
    def create(self, appuser_id, **kwargs):
        with atomic():
            order = Order()
            order.restaurant = kwargs.get('restaurant')
            order.appuser_id = appuser_id
            order.note = kwargs.get('note')
            order.save()
            self.__save_order_line_items__(order, kwargs.get('line_items'))

    def get(self, id: int):
        try:
            order = Order.objects.get(pk = id)
            return order
        except Order.DoesNotExist:
            return None

    def get_appuser_id(self, id: int):
        try:
            field_names = ('appuser_id',)
            appuser_result = self.get_fields(field_names, **{
                'id': id
            })

            return appuser_result[0]['appuser_id'] if appuser_result else None
        except Exception as e:
            print(e)

    def get_appuser_orders(self, appuser_id):
        orders = list(OrderLineItem.objects\
                        .select_related('order')
                        .filter(order__appuser_id = appuser_id)\
                        .order_by('-order__created_on'))
        return orders

    def get_todays_pending_orders(self, restaurant):
        today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
        
        q = Q()
        q &= Q(created_on__range = (today_min, today_max))
        q &= Q(restaurant_id = restaurant)
        q &= Q(status = 'Submitted')

        orders = list(Order.objects \
                        .prefetch_related('line_items') \
                        .select_related('appuser', 'restaurant', 'appuser__user') \
                        .filter(q))
        return orders

    def cancel(self, id: int):
        order = self.get(id)

        if order.status == ORDER_ACCEPTED_STATUS:
            return False, CANNOT_CHANGE_ORDER_MSG

        order.status = 'Cancelled'
        order.save()

        return True, ''

    def update(self, id: int, **kwargs):
        order = self.get(id)
        
        if order.status == ORDER_ACCEPTED_STATUS:
            return False, CANNOT_CHANGE_ORDER_MSG

        with atomic():
            order.note = kwargs.get('note')
            order.line_items.all()._raw_delete(order.line_items.db)
            order.last_updated = datetime.datetime.now()
            self.__save_order_OrderLineItems__(order, kwargs.get('line_items'))
            return True, ''

    def accept_order(self, order_id):
        order = self.get(order_id)

        if order.status == ORDER_CANCELLED_STATUS:
            return False, ORDER_CANCELLED_BY_CUSTOMER

        if order.status == ORDER_ACCEPTED_STATUS:
            return False, 'Order has already been accepted by merchant'

        order.status = ORDER_ACCEPTED_STATUS
        order.save()

        return True, ''

    def get_restaurant_id_by_orderid(self, order_id):
        field_names = ('restaurant_id',)
        restaurant_id_result = self.get_fields(field_names, ** {
            'id': order_id
        })

        return restaurant_id_result[0]['restaurant_id' if restaurant_id_result else None]

    def __build_order_line_items__(self, items, order):
        line_items = []
        for item in items:
            item['order'] = order
            item['unit_price'] = item['menu_item'].price
            item['sub_total'] = item['quantity'] * item['menu_item'].price
            detail = OrderLineItem(**item)
            line_items.append(detail)
        return line_items

    def __save_order_line_items__(self, order, line_items):
        line_items = self.__build_order_line_items__(line_items, order)
        OrderLineItem.objects.bulk_create(line_items)
        order.total = sum([d.sub_total for d in line_items])
        order.save()