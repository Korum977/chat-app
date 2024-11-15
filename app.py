from flask import Flask, render_template, jsonify, request, g
from db import Database
from auth import Auth
import sqlite3
import os
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
db = Database('chat.db')
auth = Auth(db)

# Настройки для загрузки файлов
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.errorhandler(sqlite3.OperationalError)
def handle_db_error(e):
    return jsonify({
        'error': 'Database error',
        'message': str(e)
    }), 500

@app.before_request
@auth.require_auth
def before_request():
    pass

@app.route('/')
def index():
    return render_template('index.html', chat_title="Простой чат")

@app.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.json
        if not all(k in data for k in ['email', 'password', 'username']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        user_id = db.create_user(
            email=data['email'],
            password=data['password'],
            username=data['username']
        )
        
        if user_id:
            return jsonify({'status': 'success', 'user_id': user_id})
        return jsonify({'error': 'Email already exists'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages', methods=['GET'])
def get_messages():
    messages = db.get_messages()
    return jsonify(messages)

@app.route('/api/messages', methods=['POST'])
def create_message():
    if not request.json or 'text' not in request.json:
        return jsonify({'error': 'Message text required'}), 400
    
    message_id = db.add_message(
        text=request.json['text'],
        user_id=g.user['id']  # Используем ID авторизованного пользователя
    )
    
    return jsonify({
        'status': 'success',
        'message_id': message_id
    })

@app.route('/auth/check', methods=['POST'])
def check_auth():
    auth_header = request.headers.get('Authorization')
    if auth.check_auth(auth_header):
        return jsonify({
            'status': 'success',
            'user': {
                'email': g.user['email'],
                'username': g.user['username']
            }
        })
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/users', methods=['GET'])
def get_users():
    users = db.get_users()  # Нужно добавить этот метод в класс Database
    return jsonify(users)

@app.route('/api/messages/<recipient_id>', methods=['GET'])
def get_messages_with_user(recipient_id):
    messages = db.get_messages_with_user(g.user['id'], recipient_id)
    return jsonify(messages)

@app.route('/api/messages/<recipient_id>', methods=['POST'])
def create_message_for_user(recipient_id):
    if not request.json or 'text' not in request.json:
        return jsonify({'error': 'Message text required'}), 400
    
    message_id = db.add_message(
        text=request.json['text'],
        user_id=g.user['id'],
        recipient_id=recipient_id
    )
    
    return jsonify({
        'status': 'success',
        'message_id': message_id
    })

@app.route('/upload_avatar', methods=['POST'])
def upload_avatar():
    if 'avatar' not in request.files:
        return jsonify({'success': False, 'error': 'Файл не найден'})
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Файл не выбран'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Добавляем уникальный идентификатор к имени файла
        unique_filename = f"avatar_{str(uuid.uuid4())}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Создаем директорию, если она не существует
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        file.save(filepath)
        
        # Сохраняем путь к файлу в базе данных для пользователя
        # user.avatar_url = f'/static/uploads/{unique_filename}'
        # db.session.commit()
        
        return jsonify({
            'success': True,
            'avatar_url': f'/static/uploads/{unique_filename}'
        })
    
    return jsonify({'success': False, 'error': 'Недопустимый тип файла'})

@app.route('/upload_background', methods=['POST'])
def upload_background():
    if 'background' not in request.files:
        return jsonify({'success': False, 'error': 'Файл не найден'})
    
    file = request.files['background']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Файл не выбран'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"background_{str(uuid.uuid4())}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        file.save(filepath)
        
        # Сохраняем путь к файлу в базе данных для пользователя
        # user.background_url = f'/static/uploads/{unique_filename}'
        # db.session.commit()
        
        return jsonify({
            'success': True,
            'background_url': f'/static/uploads/{unique_filename}'
        })
    
    return jsonify({'success': False, 'error': 'Недопустимый тип файла'})

if __name__ == '__main__':
    app.run(debug=True) 