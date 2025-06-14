from flask import Flask, render_template, request, redirect, url_for, session, flash
import os, json
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'lekoy_secret'

UPLOAD_FOLDER = 'static/videos'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

VIDEO_DB = 'videos.json'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'lekoy93'

def load_videos():
    if not os.path.exists(VIDEO_DB):
        return []
    with open(VIDEO_DB, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_videos(videos):
    with open(VIDEO_DB, 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    videos = load_videos()
    approved = [v for v in videos if v.get('approved', False)]
    return render_template('index.html', videos=approved)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['username'] = username
            session['is_admin'] = True
            return redirect(url_for('index'))
        else:
            flash('Sai tài khoản hoặc mật khẩu')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session.get('is_admin'):
        flash('Bạn không có quyền truy cập trang này.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        url = request.form.get('url')
        file = request.files.get('file')

        filename = None
        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            url = f'/static/videos/{filename}'

        if not url:
            flash('Cần nhập URL hoặc tải file video.')
            return redirect(url_for('upload'))

        new_video = {
            'title': title,
            'url': url,
            'category': request.form.get('category', 'Khác'),
            'approved': True,
            'uploaded_by': session.get('username', 'unknown'),
            'timestamp': datetime.utcnow().isoformat()
        }
        videos = load_videos()
        videos.append(new_video)
        save_videos(videos)

        flash('Video đã được tải lên thành công.')
        return redirect(url_for('index'))

    return render_template('upload.html')

@app.route('/category/<cat>')
def category(cat):
    videos = load_videos()
    filtered = [v for v in videos if v.get('category', '').lower() == cat.lower() and v.get('approved', False)]
    return render_template('category.html', videos=filtered, category=cat)

@app.route('/pending')
def pending():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    videos = load_videos()
    unapproved = [v for v in videos if not v.get('approved', False)]
    return render_template('pending.html', videos=unapproved)

@app.route('/approve/<int:index>')
def approve(index):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    videos = load_videos()
    if 0 <= index < len(videos):
        videos[index]['approved'] = True
        save_videos(videos)
    return redirect(url_for('pending'))
