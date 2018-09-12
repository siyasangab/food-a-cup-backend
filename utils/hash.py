import hashlib, uuid
from .app_logger import get_logger

logger = get_logger(__name__)

SEPERATOR = ':'

def hash_string(string_to_hash: str = ''):
    try:
        if not string_to_hash:
            logger.warning('No string to hash, returning None')
            return None
        logger.info('Hashing string: {string_to_hash}')
        salt = uuid.uuid4().hex
        hashed_string = hashlib.sha256(salt.encode() + string_to_hash.encode()).hexdigest() + SEPERATOR + salt
        logger.info('Successfully hashed the string!')
        return hashed_string
    except:
        logger.exception('An error occurred while hashing string: {string_to_hash}')
        return None

def validate_hash(hashed_string: str = '', plain_string: str = ''):
    if not hashed_string or not plain_string:
        return False

    if not SEPERATOR in hashed_string:
        return False

    if hashed_string.count(SEPERATOR) > 1:
        return False

    hashed, salt = hashed_string.split(SEPERATOR)
    valid = hashed == hashlib.sha256(salt.encode() + plain_string.encode()).hexdigest()

    return valid

