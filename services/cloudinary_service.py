import cloudinary
import cloudinary.uploader
import cloudinary.api

from utils.app_logger import get_logger

logger = get_logger(__name__)

def upload(file):
    logger.debug('Uploading file...')
    try:
        upload_result = cloudinary.uploader.upload(file)
        logger.debug(f'File uploaded successfully: {upload_result}')
        return upload_result
    except Exception as e:
        logger.error(f'Could not upload file: {e}')
        return ''

