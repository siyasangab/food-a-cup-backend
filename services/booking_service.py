import datetime
from django.db.models import Q
from domain.models import Booking
from .appuser_service import AppUserService
from .base.service_base import ServiceBase

class BookingService(ServiceBase):
    def __init__(self):
        super(BookingService, self).__init__(Booking)

    def get_by_appuser(self, appuser_id):
        bookings = Booking.objects.filter(Q(guest = appuser_id)).filter(~Q(status = 'Cancelled'))
        return bookings

    def create(self, user_id, **kwargs):
        guest = AppUserService().get_by_user_id(user_id)
        if guest == None:
            return None
        try:
            booking = Booking(**kwargs)
            booking.guest = guest
            booking.save()
            return booking
        except Exception as e:
            print(e)
            return None

    def update(self, id, **kwargs):
        try:
            booking = Booking.objects.get(pk = id)     
            booking.when = kwargs.get('when')
            booking.num_people = kwargs.get('num_people')
            booking.notes = kwargs.get('notes')
            booking.updated = datetime.datetime.now()
            booking.save()
            return booking
        except Exception as e:
            print(e)
            return None

    def delete(self, id):
        try:
            booking = Booking.objects.get(pk = id)
            if booking.status == 'Cancelled':
                return False
                
            booking.status = 'Cancelled'
            booking.updated = datetime.datetime.now()
            booking.save()
            return True
        except Exception as e:
            print(e)
            return False

