import os
import sys

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from app.core.containers import Container

def create_app() -> Flask:
    app = Flask(__name__)
    
    # Создаем и конфигурируем контейнер
    container = Container()
    
    # Инициализируем сервисы
    auth_service = container.auth_service()
    user_service = container.user_service()
    message_service = container.message_service()
    file_service = container.file_service()
    
    # Регистрируем маршруты
    from app.routes import register_routes
    register_routes(app, auth_service, user_service, message_service, file_service)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)