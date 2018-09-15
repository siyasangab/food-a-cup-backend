from django.db.models import Q

from .base.service_base import ServiceBase
from .appuser_service import AppUserService
from utils.app_logger import get_logger
from utils.hash import hash_string, validate_hash
from domain.models import ChatRoom, ChatMessage

logger = get_logger(__name__)

class ChatService(ServiceBase):
    def __init__(self):
        self._appuser_service = AppUserService()
        pass

    def get_chatroom_by_name(self, name: str = '', include_messages: bool = False):      
        if not name:
            logger.warning(f'Invalid chatroom name')
            return None
        try:
            logger.info(f'Getting chatroom {name}')
            if not include_messages:
                chat_room = ChatRoom.objects.get(name = name)
            else:
                chat_room = ChatRoom.objects.prefetch_related('messages').get(name = name)
            return chat_room
        except ChatRoom.DoesNotExist:
            logger.exception(f'Chatroom {name} not found')
            return 

    def create_chatroom(self, from_email: str = '', to_email: str = ''):
        if not from_email or not to_email:
            logger.error(f'Can\'t create chatroom, between {from_email} and {to_email}')
            return None

        logger.error(f'Creating chatroom, between {from_email} and {to_email}')
        creator = self._appuser_service.get(email = from_email, by = 'email')
        other_user = self._appuser_service.get(email = to_email, by = 'email')

        from_to = f'{from_email}, {to_email}'
        chatroom_name = hash_string(from_to)

        if not creator or not other_user:
            return False

        chatroom = ChatRoom()
        chatroom.created_by = creator
        chatroom.other_user = other_user
        chatroom.name = chatroom_name
        chatroom.save()
        return chatroom

    def create(self, chatroom_name: str, message: str = '', from_email: str = '', to_email: str = ''):
        if not chatroom_name or not message or not from_email or not to_email:
            return False
        from_to = f'{from_email}, {to_email}'

        valid_chatroom = validate_hash(chatroom_name, from_to)
        if not valid_chatroom:
            return None

        chatroom = self.get_chatroom_by_name(chatroom_name)

        chat_message = ChatMessage()
        chat_message.chat_room = chatroom
        chat_message.sender = self._appuser_service.get(email = from_email, by = 'email')
        chat_message.receiver = self._appuser_service.get(email = to_email, by = 'email')
        chat_message.message = message
        chat_message.save()

        return True

    def get_messages(self, chatroom_name: str = ''):
        if not chatroom_name:
            return None

        chatroom = self.get_chatroom_by_name(chatroom_name, include_messages=True)
        if not chatroom:
            return None

        return list(chatroom.messages.all())

    def get_appuser_chatrooms(self, appuser_id):
        if not appuser_id or not isinstance(appuser_id, int):
            logger.error('Invalid appuser id: {appuser_id}')
            return
        try:
            logger.info(f'Getting chatrooms for appuser {appuser_id}')
            q = Q()
            q |= Q(created_by_id = appuser_id)
            q |= Q(other_user_id = appuser_id)
            chatrooms = list(ChatRoom.objects.filter(q))
            return chatrooms
        except Exception:
            logger.exception(f'Could not get appuser {appuser_id} chatrooms')
            return None