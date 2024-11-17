from dependency_injector import containers, providers
from app.core.config import Config
from app.repositories.user_repository import UserRepository
from app.repositories.message_repository import MessageRepository
from app.services.user_service import UserService
from app.services.message_service import MessageService
from app.services.file_service import FileService
from app.services.auth_service import AuthService

class Container(containers.DeclarativeContainer):
    # Configuration
    config = providers.Singleton(Config.get_instance)
    
    # Repositories
    user_repository = providers.Singleton(
        UserRepository,
        db_name=config.provided.DB_NAME
    )
    
    message_repository = providers.Singleton(
        MessageRepository,
        db_name=config.provided.DB_NAME
    )
    
    # Services
    file_service = providers.Singleton(
        FileService,
        upload_folder=config.provided.UPLOAD_FOLDER,
        allowed_extensions=config.provided.ALLOWED_EXTENSIONS
    )
    
    user_service = providers.Singleton(
        UserService,
        user_repository=user_repository,
        file_service=file_service
    )
    
    message_service = providers.Singleton(
        MessageService,
        message_repository=message_repository
    )
    
    auth_service = providers.Singleton(
        AuthService,
        user_repository=user_repository
    ) 