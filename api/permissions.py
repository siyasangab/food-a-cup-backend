from rest_framework import permissions

from services.appuser_service import AppUserService
from services.order_service import OrderService

class Customer(permissions.BasePermission):
    def __init__(self):
        self.__appuser_service = AppUserService()
        
    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name='Customer'):
            appuser_id = self.__appuser_service.get_appuser_id_by_user_id(request.user.id)
            if not appuser_id:
                return False
            request.appuser_id = appuser_id
            return True
        return False

class CanChangeOrder(permissions.BasePermission):
    def __init__(self):
        self.__order_service = OrderService()

    def has_permission(self, request, view):
        if not request.user:
            return False

        order_id = view.kwargs.get('order_id')
        if not order_id:
            return False

        order_appuser_id = self.__order_service.get_appuser_id(order_id)
        if not order_appuser_id or order_appuser_id != request.appuser_id:
            return False

        return True

