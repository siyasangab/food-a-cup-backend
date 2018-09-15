import urllib
from utils.app_logger import get_logger

logger = get_logger(__name__)

class NotificationService:
    @staticmethod
    def send_sms(self, to: str = '', msg: str = ''):
        if not to or not msg:
            return False

        url = ''
        params = urllib.urlencode({
            'username': '',
            'password': '',
            'message': '',
            'msisdn': ''
        })

        f = urllib.urlopen(url, params)
        s = f.read()

        result = s.split('|')
        status_code = result[0]
        status_string = result[1]

        if status_code != '0':
            logger.error(f'Failed to send sms notification to {to}. Reason - Status code: {status_code}, Description: {status_string}')
            return False

        

        

        