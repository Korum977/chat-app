import os
from werkzeug.utils import secure_filename
import uuid
from typing import Optional, Tuple
import hashlib

class FileService:
    def __init__(self, upload_folder: str, allowed_extensions: set):
        self.upload_folder = upload_folder
        self.allowed_extensions = allowed_extensions

    def allowed_file(self, filename: str) -> bool:
        """Проверяет допустимость расширения файла"""
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def get_user_folder(self, email: str) -> str:
        """Создает путь к папке пользователя на основе email"""
        email_hash = hashlib.md5(email.encode()).hexdigest()
        return os.path.join(self.upload_folder, email_hash)

    def save_file(self, file, email: str = '', prefix: str = '') -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Сохраняет файл в папку пользователя и возвращает кортеж (успех, url, ошибка)
        
        Args:
            file: Файл из request.files
            email: Email пользователя для организации структуры папок
            prefix: Префикс для имени файла
            
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: (успех, url файла, текст ошибки)
        """
        if not file or file.filename == '':
            return False, None, 'No file selected'
            
        if not self.allowed_file(file.filename):
            return False, None, 'Invalid file type'
            
        try:
            # Определяем папку для сохранения
            save_folder = self.get_user_folder(email) if email else self.upload_folder
            os.makedirs(save_folder, exist_ok=True)
            
            # Генерируем уникальное имя файла
            filename = secure_filename(file.filename)
            unique_filename = f"{prefix}{str(uuid.uuid4())}_{filename}"
            
            # Полный путь к файлу
            filepath = os.path.join(save_folder, unique_filename)
            
            # Сохраняем файл
            file.save(filepath)
            
            # Формируем URL для доступа к файлу
            # Получаем путь относительно static директории
            static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static')
            relative_path = os.path.relpath(filepath, static_dir).replace('\\', '/')
            file_url = f'/static/{relative_path}'
            
            return True, file_url, None
            
        except Exception as e:
            return False, None, str(e)

    def remove_file(self, file_url: str) -> bool:
        """
        Удаляет файл по его URL
        
        Args:
            file_url: URL файла для удаления
            
        Returns:
            bool: Успешность удаления
        """
        try:
            if not file_url:
                return True
                
            # Преобразуем URL в путь к файлу
            relative_path = file_url.split('/static/')[1]
            static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static')
            file_path = os.path.join(static_dir, relative_path)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                
                # Пытаемся удалить пустую папку пользователя
                folder = os.path.dirname(file_path)
                if not os.listdir(folder):
                    os.rmdir(folder)
                    
            return True
            
        except Exception:
            return False 