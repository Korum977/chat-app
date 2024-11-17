from flask import Flask, render_template, jsonify, request, g, send_from_directory
from app.core.config import Config
from app.services.auth_service import AuthService
from app.services.file_service import FileService
from app.services.user_service import UserService
from app.services.message_service import MessageService
import sqlite3

def register_routes(
    app: Flask,
    auth_service: AuthService,
    user_service: UserService,
    message_service: MessageService,
    file_service: FileService
):
    @app.errorhandler(sqlite3.OperationalError)
    def handle_db_error(e):
        return jsonify({
            'error': 'Database error',
            'message': str(e)
        }), 500

    @app.before_request
    @auth_service.require_auth
    def before_request():
        pass

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/auth/register', methods=['POST'])
    def register():
        try:
            data = request.json
            if not all(k in data for k in ['email', 'password', 'username']):
                return jsonify({'error': 'Missing required fields'}), 400
            
            success, user_id, error = user_service.register(
                email=data['email'],
                password=data['password'],
                username=data['username']
            )
            
            if success:
                return jsonify({'status': 'success', 'user_id': user_id})
            return jsonify({'error': error}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/auth/check', methods=['POST'])
    def check_auth():
        auth_header = request.headers.get('Authorization')
        if auth_service.check_auth(auth_header):
            return jsonify({
                'status': 'success',
                'user': {
                    'email': g.user.email,
                    'username': g.user.username,
                    'avatar_url': g.user.avatar_url,
                    'id': g.user.id
                }
            })
        return jsonify({'error': 'Invalid credentials'}), 401

    @app.route('/api/users', methods=['GET'])
    def get_users():
        users = user_service.get_all_users()
        return jsonify([{
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'avatar_url': user.avatar_url,
            'created_at': user.created_at.isoformat() if user.created_at else None
        } for user in users])

    @app.route('/api/messages/<recipient_id>', methods=['GET'])
    def get_messages_with_user(recipient_id):
        try:
            messages = message_service.get_conversation(g.user.id, recipient_id)
            return jsonify([{
                'id': msg.id,
                'text': msg.text,
                'user_id': msg.user_id,
                'recipient_id': msg.recipient_id,
                'username': msg.username,
                'avatar_url': msg.avatar_url,
                'timestamp': msg.timestamp.isoformat(),
                'reply_to': {
                    'id': msg.reply_to.id,
                    'text': msg.reply_to.text,
                    'username': msg.reply_to.username
                } if msg.reply_to else None,
                'is_mine': msg.is_mine
            } for msg in messages])
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/messages/<recipient_id>', methods=['POST'])
    def create_message_for_user(recipient_id):
        try:
            if not request.json or 'text' not in request.json:
                return jsonify({'error': 'Message text required'}), 400
            
            success, message, error = message_service.create_message(
                text=request.json['text'],
                sender=g.user,
                recipient_id=recipient_id,
                reply_to_id=request.json.get('reply_to_id')
            )
            
            if success and message:
                return jsonify({
                    'id': message.id,
                    'text': message.text,
                    'user_id': message.user_id,
                    'recipient_id': message.recipient_id,
                    'username': message.username,
                    'avatar_url': message.avatar_url,
                    'timestamp': message.timestamp.isoformat(),
                    'reply_to': {
                        'id': message.reply_to.id,
                        'text': message.reply_to.text,
                        'username': message.reply_to.username
                    } if message.reply_to else None,
                    'is_mine': True
                })
            
            return jsonify({'error': error}), 400
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/messages/<message_id>', methods=['DELETE'])
    def delete_message(message_id):
        try:
            success, error = message_service.delete_message(int(message_id), g.user.id)
            if success:
                return jsonify({'status': 'success'})
            return jsonify({'error': error}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/get_avatar', methods=['GET'])
    @auth_service.require_auth
    def get_avatar():
        return jsonify({
            'success': True,
            'avatar_url': g.user.avatar_url
        })

    @app.route('/upload_avatar', methods=['POST'])
    @auth_service.require_auth
    def upload_avatar():
        if 'avatar' not in request.files:
            return jsonify({'success': False, 'error': 'No file found'})
        
        success, file_url, error = user_service.update_avatar(
            user=g.user,
            avatar_file=request.files['avatar']
        )
        
        if success:
            return jsonify({
                'success': True,
                'avatar_url': file_url
            })
        
        return jsonify({'success': False, 'error': error})

    @app.route('/remove_avatar', methods=['POST'])
    @auth_service.require_auth
    def remove_avatar():
        if user_service.remove_avatar(g.user):
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Failed to remove avatar'})

    @app.route('/upload_background', methods=['POST'])
    @auth_service.require_auth
    def upload_background():
        if 'background' not in request.files:
            return jsonify({'success': False, 'error': 'No file found'})
        
        success, file_url, error = file_service.save_file(
            request.files['background'], 
            prefix='background_'
        )
        
        if success:
            return jsonify({
                'success': True,
                'background_url': file_url
            })
        
        return jsonify({'success': False, 'error': error})

    @app.route('/static/uploads/<path:filename>')
    def serve_upload(filename):
        """Специальный маршрут для отдачи загруженных файлов"""
        return send_from_directory(Config.get_upload_path(), filename)