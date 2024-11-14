from functools import wraps
from flask import request, jsonify, g
import base64

class Auth:
    def __init__(self, db):
        self.db = db

    def check_auth(self, auth_header):
        """Проверяет Basic Auth заголовок"""
        if not auth_header or not auth_header.startswith('Basic '):
            return False

        try:
            # Декодируем Base64 credentials
            encoded = auth_header.split(' ')[1]
            decoded = base64.b64decode(encoded).decode('utf-8')
            email, password = decoded.split(':')
            
            # Проверяем учетные данные в базе
            user = self.db.verify_user(email, password)
            if user:
                # Сохраняем пользователя в g для использования в запросе
                g.user = user
                return True
            return False
        except Exception:
            return False

    def require_auth(self, f):
        """Декоратор для проверки авторизации API endpoints"""
        @wraps(f)
        def decorated(*args, **kwargs):
            # Проверяем только API endpoints
            if request.path.startswith('/api/'):
                auth_header = request.headers.get('Authorization')
                if not self.check_auth(auth_header):
                    return jsonify({
                        'error': 'Unauthorized',
                        'message': 'Please provide valid credentials'
                    }), 401
            return f(*args, **kwargs)
        return decorated