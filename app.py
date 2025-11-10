from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import uuid
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'arbtube-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///arbtube.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['VIDEO_FOLDER'] = 'uploads/videos'
app.config['THUMBNAIL_FOLDER'] = 'uploads/thumbnails'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'}

# Создаем необходимые директории
for folder in [app.config['UPLOAD_FOLDER'], app.config['VIDEO_FOLDER'], app.config['THUMBNAIL_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Модели базы данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    channel_name = db.Column(db.String(100))
    avatar = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    videos = db.relationship('Video', backref='author', lazy=True)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(255), nullable=False)
    thumbnail = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.String(20))
    comments = db.relationship('Comment', backref='video', lazy=True, cascade='all, delete-orphan')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='comments')

class VideoHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    watched_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='history')
    video = db.relationship('Video', backref='history_entries')

class VideoLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    is_like = db.Column(db.Boolean, default=True)  # True = like, False = dislike
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='likes')
    video = db.relationship('Video', backref='like_entries')
    __table_args__ = (db.UniqueConstraint('user_id', 'video_id', name='unique_user_video_like'),)

class WatchLater(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='watch_later')
    video = db.relationship('Video', backref='watch_later_entries')
    __table_args__ = (db.UniqueConstraint('user_id', 'video_id', name='unique_user_video_watch_later'),)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subscriber_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    subscriber = db.relationship('User', foreign_keys=[subscriber_id], backref='subscriptions')
    channel = db.relationship('User', foreign_keys=[channel_id], backref='subscribers')
    __table_args__ = (db.UniqueConstraint('subscriber_id', 'channel_id', name='unique_subscription'),)

# Создаем таблицы
# with app.app_context():
#     db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Роуты
@app.route('/')
def index():
    query = request.args.get('q', '')
    if query:
        videos = Video.query.filter(
            or_(
                Video.title.contains(query),
                Video.description.contains(query)
            )
        ).order_by(Video.created_at.desc()).limit(20).all()
    else:
        videos = Video.query.order_by(Video.created_at.desc()).limit(20).all()
    return render_template('index.html', videos=videos, search_query=query)

@app.route('/watch/<int:video_id>')
def watch(video_id):
    video = Video.query.get_or_404(video_id)
    video.views += 1
    
    # Добавляем в историю просмотров
    if 'user_id' in session:
        # Проверяем, есть ли уже запись в истории
        existing_history = VideoHistory.query.filter_by(
            user_id=session['user_id'],
            video_id=video_id
        ).first()
        
        if existing_history:
            existing_history.watched_at = datetime.utcnow()
        else:
            history = VideoHistory(user_id=session['user_id'], video_id=video_id)
            db.session.add(history)
    
    db.session.commit()
    
    # Получаем похожие видео
    related_videos = Video.query.filter(Video.id != video_id).order_by(Video.created_at.desc()).limit(10).all()
    is_own_video = 'user_id' in session and session['user_id'] == video.user_id
    
    # Проверяем, лайкнул ли пользователь видео
    is_liked = False
    is_disliked = False
    if 'user_id' in session:
        like = VideoLike.query.filter_by(user_id=session['user_id'], video_id=video_id).first()
        if like:
            is_liked = like.is_like
            is_disliked = not like.is_like
    
    # Проверяем, подписан ли пользователь на автора
    is_subscribed = False
    if 'user_id' in session and not is_own_video:
        subscription = Subscription.query.filter_by(subscriber_id=session['user_id'], channel_id=video.user_id).first()
        is_subscribed = subscription is not None
    
    return render_template('watch.html', video=video, related_videos=related_videos, 
                         is_own_video=is_own_video, is_liked=is_liked, is_disliked=is_disliked, is_subscribed=is_subscribed)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            if 'video' not in request.files:
                return jsonify({'error': 'Файл видео не выбран'}), 400
            
            file = request.files['video']
            if file.filename == '':
                return jsonify({'error': 'Файл не выбран'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'error': 'Неподдерживаемый формат файла. Используйте: MP4, AVI, MOV, WMV, FLV, WEBM'}), 400
            
            # Проверка размера файла
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > app.config['MAX_CONTENT_LENGTH']:
                return jsonify({'error': 'Файл слишком большой. Максимальный размер: 500MB'}), 400
            
            filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
            filepath = os.path.join(app.config['VIDEO_FOLDER'], filename)
            file.save(filepath)
            
            title = request.form.get('title', 'Без названия')
            if not title or title.strip() == '':
                title = 'Без названия'
            
            description = request.form.get('description', '')
            
            # Обработка превью (миниатюры)
            thumbnail_filename = None
            if 'thumbnail' in request.files:
                thumbnail_file = request.files['thumbnail']
                if thumbnail_file and thumbnail_file.filename != '':
                    # Проверяем, что это изображение
                    if thumbnail_file.content_type and thumbnail_file.content_type.startswith('image/'):
                        thumbnail_ext = thumbnail_file.filename.rsplit('.', 1)[1].lower() if '.' in thumbnail_file.filename else 'jpg'
                        if thumbnail_ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                            return jsonify({'error': 'Неподдерживаемый формат изображения. Используйте: JPG, PNG, GIF, WEBP'}), 400
                        
                        thumbnail_filename = str(uuid.uuid4()) + '.' + thumbnail_ext
                        thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumbnail_filename)
                        thumbnail_file.save(thumbnail_path)
            
            video = Video(
                title=title,
                description=description,
                filename=filename,
                user_id=session['user_id'],
                thumbnail=thumbnail_filename
            )
            
            db.session.add(video)
            db.session.commit()
            
            return jsonify({'success': True, 'video_id': video.id})
        except Exception as e:
            return jsonify({'error': f'Ошибка загрузки: {str(e)}'}), 500
    
    return render_template('upload.html')

@app.route('/videos/<filename>')
def video_file(filename):
    return send_from_directory(app.config['VIDEO_FOLDER'], filename)

@app.route('/thumbnails/<filename>')
def thumbnail_file(filename):
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename)

@app.route('/api/videos')
def api_videos():
    videos = Video.query.order_by(Video.created_at.desc()).all()
    return jsonify([{
        'id': v.id,
        'title': v.title,
        'thumbnail': v.thumbnail or '/static/default-thumbnail.jpg',
        'author': v.author.username,
        'views': v.views,
        'created_at': v.created_at.isoformat()
    } for v in videos])

@app.route('/api/video/<int:video_id>')
def api_video(video_id):
    video = Video.query.get_or_404(video_id)
    return jsonify({
        'id': video.id,
        'title': video.title,
        'description': video.description,
        'filename': video.filename,
        'author': video.author.username,
        'views': video.views,
        'likes': video.likes,
        'created_at': video.created_at.isoformat()
    })

@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    videos = Video.query.filter(
        or_(
            Video.title.contains(query),
            Video.description.contains(query)
        )
    ).all()
    
    return jsonify([{
        'id': v.id,
        'title': v.title,
        'thumbnail': v.thumbnail or '/static/default-thumbnail.jpg',
        'author': v.author.username,
        'views': v.views,
        'created_at': v.created_at.isoformat()
    } for v in videos])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            channel_name=username
        )
        
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        session['username'] = user.username
        
        return jsonify({'success': True, 'user_id': user.id})
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return jsonify({'success': True, 'user_id': user.id})
        
        return jsonify({'error': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/channel/<username>')
def channel(username):
    user = User.query.filter_by(username=username).first_or_404()
    videos = Video.query.filter_by(user_id=user.id).order_by(Video.created_at.desc()).all()
    is_own_channel = 'user_id' in session and session['user_id'] == user.id
    
    # Проверяем, подписан ли пользователь на канал
    is_subscribed = False
    if 'user_id' in session and not is_own_channel:
        subscription = Subscription.query.filter_by(subscriber_id=session['user_id'], channel_id=user.id).first()
        is_subscribed = subscription is not None
    
    return render_template('channel.html', user=user, videos=videos, is_own_channel=is_own_channel, is_subscribed=is_subscribed)

@app.route('/channel/settings', methods=['GET', 'POST'])
def channel_settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        data = request.json
        channel_name = data.get('channel_name', '').strip()
        
        if channel_name:
            user.channel_name = channel_name
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Настройки сохранены', 'username': user.username})
    
    return render_template('channel_settings.html', user=user)

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    history_entries = VideoHistory.query.filter_by(user_id=session['user_id']).order_by(VideoHistory.watched_at.desc()).limit(50).all()
    videos = [entry.video for entry in history_entries]
    return render_template('history.html', videos=videos)

@app.route('/liked')
def liked():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    likes = VideoLike.query.filter_by(user_id=session['user_id'], is_like=True).order_by(VideoLike.created_at.desc()).all()
    videos = [like.video for like in likes]
    return render_template('liked.html', videos=videos)

@app.route('/watch-later')
def watch_later():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    watch_later_entries = WatchLater.query.filter_by(user_id=session['user_id']).order_by(WatchLater.added_at.desc()).all()
    videos = [entry.video for entry in watch_later_entries]
    return render_template('watch_later.html', videos=videos)

@app.route('/library')
def library():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('library.html')

@app.route('/subscriptions')
def subscriptions():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    subscriptions_list = Subscription.query.filter_by(subscriber_id=session['user_id']).all()
    channels = [sub.channel for sub in subscriptions_list]
    return render_template('subscriptions.html', channels=channels)

@app.route('/shorts')
def shorts():
    return render_template('shorts.html')

@app.route('/studio')
def studio():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    # Получаем все видео пользователя
    videos = Video.query.filter_by(user_id=user.id).order_by(Video.created_at.desc()).all()
    
    # Статистика канала
    total_views = sum(v.views for v in videos)
    total_likes = sum(v.likes for v in videos)
    total_videos = len(videos)
    subscribers_count = Subscription.query.filter_by(channel_id=user.id).count()
    
    return render_template('studio.html', user=user, videos=videos, 
                         total_views=total_views, total_likes=total_likes, 
                         total_videos=total_videos, subscribers_count=subscribers_count)

@app.route('/api/studio/delete/<int:video_id>', methods=['POST'])
def delete_video(video_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    video = Video.query.get_or_404(video_id)
    
    # Проверяем, что видео принадлежит пользователю
    if video.user_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Удаляем связанные записи (каскадное удаление)
        # Комментарии удалятся автоматически благодаря cascade='all, delete-orphan'
        # Но нужно удалить вручную историю, лайки и watch_later
        
        # Удаляем историю просмотров
        VideoHistory.query.filter_by(video_id=video_id).delete()
        
        # Удаляем лайки
        VideoLike.query.filter_by(video_id=video_id).delete()
        
        # Удаляем из "Смотреть позже"
        WatchLater.query.filter_by(video_id=video_id).delete()
        
        # Удаляем файлы
        if video.filename:
            video_path = os.path.join(app.config['VIDEO_FOLDER'], video.filename)
            if os.path.exists(video_path):
                try:
                    os.remove(video_path)
                except Exception as e:
                    print(f"Error deleting video file: {e}")
        
        if video.thumbnail:
            thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], video.thumbnail)
            if os.path.exists(thumbnail_path):
                try:
                    os.remove(thumbnail_path)
                except Exception as e:
                    print(f"Error deleting thumbnail file: {e}")
        
        # Удаляем видео из базы данных
        db.session.delete(video)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Видео успешно удалено'})
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting video: {e}")
        return jsonify({'error': f'Ошибка при удалении видео: {str(e)}'}), 500

@app.route('/api/like/<int:video_id>', methods=['POST'])
def like_video(video_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    video = Video.query.get_or_404(video_id)
    data = request.json
    is_like = data.get('is_like', True)
    
    # Проверяем, есть ли уже лайк
    existing_like = VideoLike.query.filter_by(user_id=session['user_id'], video_id=video_id).first()
    
    if existing_like:
        if existing_like.is_like == is_like:
            # Удаляем лайк/дизлайк если нажали на тот же
            db.session.delete(existing_like)
            if is_like:
                video.likes = max(0, video.likes - 1)
            else:
                video.dislikes = max(0, video.dislikes - 1)
        else:
            # Меняем лайк на дизлайк или наоборот
            existing_like.is_like = is_like
            if is_like:
                video.likes += 1
                video.dislikes = max(0, video.dislikes - 1)
            else:
                video.dislikes += 1
                video.likes = max(0, video.likes - 1)
    else:
        # Создаем новый лайк
        like = VideoLike(user_id=session['user_id'], video_id=video_id, is_like=is_like)
        db.session.add(like)
        if is_like:
            video.likes += 1
        else:
            video.dislikes += 1
    
    db.session.commit()
    return jsonify({'success': True, 'likes': video.likes, 'dislikes': video.dislikes})

@app.route('/api/watch-later/<int:video_id>', methods=['POST'])
def add_watch_later(video_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Проверяем, есть ли уже в списке
    existing = WatchLater.query.filter_by(user_id=session['user_id'], video_id=video_id).first()
    
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'success': True, 'added': False})
    else:
        watch_later = WatchLater(user_id=session['user_id'], video_id=video_id)
        db.session.add(watch_later)
        db.session.commit()
        return jsonify({'success': True, 'added': True})

@app.route('/api/subscribe/<username>', methods=['POST'])
def subscribe(username):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    channel = User.query.filter_by(username=username).first_or_404()
    
    if channel.id == session['user_id']:
        return jsonify({'error': 'Cannot subscribe to yourself'}), 400
    
    # Проверяем, подписан ли уже
    existing = Subscription.query.filter_by(subscriber_id=session['user_id'], channel_id=channel.id).first()
    
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'success': True, 'subscribed': False})
    else:
        subscription = Subscription(subscriber_id=session['user_id'], channel_id=channel.id)
        db.session.add(subscription)
        db.session.commit()
        return jsonify({'success': True, 'subscribed': True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
