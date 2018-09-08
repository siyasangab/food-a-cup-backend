import googlemaps
from django.conf import settings

from utils.app_logger import get_logger

logger = get_logger(__name__)

def get_latlng(place = ''):
    if place == None or place.strip() == '':
        return None, None

    try:
        logger.debug(f'Geocoding place: {place}')
        gm = googlemaps.Client(key = settings.GOOGLE_API_KEY)
        geocode_result = gm.geocode(place)
        location = geocode_result[0]['geometry']['location']
        lat, lng = location['lat'], location['lng']
        logger.debug(f'{place} successfully geocoded: {lat}, lng')
        return lat, lng
    except Exception as e:
        logger.exception(f'Could not geocode {place}')
        return None, None