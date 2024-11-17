from typing import List, Optional, Tuple
from app.repositories.message_repository import MessageRepository
from app.models.domain.message import Message
from app.models.domain.user import User

class MessageService:
    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    def create_message(
        self, 
        text: str, 
        sender: User, 
        recipient_id: str, 
        reply_to_id: Optional[int] = None
    ) -> Tuple[bool, Optional[Message], Optional[str]]:
        try:
            # Проверяем существование сообщения, на которое отвечаем
            if reply_to_id:
                reply_message = self.message_repository.get_by_id(reply_to_id)
                if not reply_message:
                    return False, None, "Reply message not found"
                
                # Проверяем, что отвечаем на сообщение из этого же диалога
                if not (
                    (reply_message.user_id == sender.id and reply_message.recipient_id == recipient_id) or
                    (reply_message.user_id == recipient_id and reply_message.recipient_id == sender.id)
                ):
                    return False, None, "Cannot reply to message from another conversation"
            
            # Создаем новое сообщение
            message_id = self.message_repository.create(
                text=text,
                user_id=sender.id,
                recipient_id=recipient_id,
                reply_to_id=reply_to_id
            )
            
            # Получаем созданное сообщение со всеми связанными данными
            new_message = self.message_repository.get_by_id(message_id)
            if new_message:
                return True, new_message, None
                
            return False, None, "Failed to create message"
            
        except Exception as e:
            return False, None, str(e)

    def get_conversation(self, user_id: str, other_user_id: str, limit: int = 100) -> List[Message]:
        """
        Получает диалог между двумя пользователями с информацией об ответах
        
        Args:
            user_id: ID текущего пользователя
            other_user_id: ID собеседника
            limit: Максимальное количество сообщений
            
        Returns:
            List[Message]: Список сообщений с информацией об ответах
        """
        return self.message_repository.get_conversation(user_id, other_user_id, limit)

    def delete_message(self, message_id: int, user_id: str) -> Tuple[bool, Optional[str]]:
        """
        Удаляет сообщение, если оно принадлежит пользователю
        
        Args:
            message_id: ID сообщения
            user_id: ID пользователя, который пытается удалить сообщение
            
        Returns:
            Tuple[bool, Optional[str]]: (успех, текст ошибки)
        """
        message = self.message_repository.get_by_id(message_id)
        
        if not message:
            return False, "Message not found"
            
        if message.user_id != user_id:
            return False, "Not authorized to delete this message"
            
        if self.message_repository.delete(message_id):
            return True, None
            
        return False, "Failed to delete message" 