from typing import Optional, List, Tuple
from app.repositories.user_repository import UserRepository
from app.models.domain.user import User
from app.services.file_service import FileService

class UserService:
    def __init__(self, user_repository: UserRepository, file_service: FileService):
        self.user_repository = user_repository
        self.file_service = file_service

    def register(self, email: str, password: str, username: str) -> Tuple[bool, Optional[str], Optional[str]]:
        try:
            user_id = self.user_repository.create(email, password, username)
            if user_id:
                return True, user_id, None
            return False, None, "Email already exists"
        except Exception as e:
            return False, None, str(e)

    def verify_credentials(self, email: str, password: str) -> Optional[User]:
        return self.user_repository.verify(email, password)

    def get_all_users(self) -> List[User]:
        return self.user_repository.get_all()

    def update_avatar(self, user: User, avatar_file) -> Tuple[bool, Optional[str], Optional[str]]:
        # Сохраняем новый файл
        success, file_url, error = self.file_service.save_file(
            avatar_file,
            email=user.email,
            prefix='avatar_'
        )
        
        if not success:
            return False, None, error

        # Удаляем старый аватар
        if user.avatar_url:
            self.file_service.remove_file(user.avatar_url)

        # Обновляем URL в базе данных
        self.user_repository.update_avatar(user.id, file_url)
        
        return True, file_url, None

    def remove_avatar(self, user: User) -> bool:
        if user.avatar_url:
            if self.file_service.remove_file(user.avatar_url):
                self.user_repository.update_avatar(user.id, None)
                return True
        return False 