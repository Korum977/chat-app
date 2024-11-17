from functools import wraps
from flask import request, g, jsonify
import base64
from app.repositories.user_repository import UserRepository

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def check_auth(self, auth_header: str) -> bool:
        """Проверяет Basic Auth заголовок"""
        if not auth_header:
            return False
            
        try:
            auth_type, auth_string = auth_header.split(' ', 1)
            if auth_type.lower() != 'basic':
                return False
                
            auth_decoded = base64.b64decode(auth_string).decode('utf-8')
            email, password = auth_decoded.split(':', 1)
            
            user = self.user_repository.verify(email, password)
            if user:
                g.user = user
                return True
        except Exception:
            pass
            
        return False

    def require_auth(self, f):
        """Декоратор для защиты маршрутов"""
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            # Пропускаем проверку для некоторых маршрутов
            if request.endpoint in ['index', 'register', 'check_auth'] or request.path.startswith('/static/uploads/'):
                return f(*args, **kwargs)
                
            if not self.check_auth(auth_header):
                return jsonify({'error': 'Unauthorized'}), 401
                
            return f(*args, **kwargs)
        return decorated 