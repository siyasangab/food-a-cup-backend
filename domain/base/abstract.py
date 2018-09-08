from django.db import models
from domain.utils import get_unique_slug

class Place(models.Model):
    '''
        Base class for different types of places. E.g. restaurants and liquour outlets
    '''
    name = models.CharField(max_length = 50, db_index = True)
    slug = models.SlugField(max_length = 100, db_index = True, unique = True)
    address_line1 = models.CharField(max_length = 50)
    address_line2 = models.CharField(max_length = 50, default = '', null = True, blank = True)
    tagline = models.CharField(max_length = 150, default = '', null = True, blank = True)
    banner_url = models.URLField(max_length = 200)
    suburb = models.CharField(max_length = 50, db_index = True)
    phone = models.CharField(max_length = 10)
    email = models.EmailField(max_length = 100, null = True, blank = True)
    website = models.URLField(max_length = 100, null = True, blank = True)
    latitude = models.DecimalField(max_digits = 20, decimal_places=16)
    longitude = models.DecimalField(max_digits = 20, decimal_places=16)
    city = models.CharField(max_length = 50, db_index = True)
    active = models.BooleanField(default = False, db_index = False)
    created_on = models.DateTimeField(auto_now_add = True)
    last_updated = models.DateTimeField(auto_now_add = True)

    class Meta:
        abstract = True
        index_together = ('longitude', 'latitude')

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug(self, 'name', 'slug')
        super().save(*args, **kwargs)


DAYS = ((0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'))
class OperatingHours(models.Model):
    '''
        Abstract class for a place's operating hours
    '''
    day = models.IntegerField(choices = DAYS, db_index = True)
    opens = models.TimeField()
    closes = models.TimeField()

    class Meta:
        abstract = True

class Category(models.Model):
    '''
        Abstract class for a merchant's inventory categories
    '''
    name = models.CharField(max_length = 50, db_index = True)
    slug = models.SlugField(max_length = 100, db_index = True, blank = True)
    created_on = models.DateTimeField(auto_now_add = True)
    last_updated = models.DateTimeField(auto_now_add = True)

    class Meta:
        abstract = True
        ordering = ('name',)

class MenuItem(models.Model):
    name = models.CharField(max_length = 50, db_index = True)
    slug = models.SlugField(max_length = 100, db_index = True, blank = True)
    price = models.DecimalField(max_digits = 6, decimal_places = 2)
    active = models.BooleanField(default = True, db_index = True)
    created_on = models.DateTimeField(auto_now_add = True)
    last_updated = models.DateTimeField(auto_now_add = True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug(self, 'name', 'slug')
        super().save(*args, **kwargs)