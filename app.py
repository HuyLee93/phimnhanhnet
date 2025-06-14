from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'lekoy_secret'

VIDEO_JSON = 'videos.json'
UPLOAD_FOLDER = 'static/videos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Tài khoản mặc định
ACCOUNTS = {
    'admin': {'password': 'lekoy93', 'is_admin': True},
    'guest': {'password': 'guest', 'is_admin': False}
}

# Load video từ file JSON
def load_videos():
    if os.path.exists(VIDEO_JSON):
        with open(VIDEO_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Lưu video vào file JSON
def save_videos(videos):
    with open(VIDEO_JSON, 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    videos = load_videos()
    approved_videos = [v for v in videos if v.get('approved')]
    return render_template('index.html', videos=approved_videos)

@app.route('/category/<cat>')
def category(cat):
    videos = load_videos()
    filtered = [v for v in videos if v.get('approved') and v.get('category') == cat]
    return render_template('category.html', videos=filtered, category=cat)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        url = request.form['url']
        category = request.form['category']
        video = {
            'title': title,
            'url': url,
            'category': category,
            'approved': True,
            'uploader': session['username'],
            'uploaded_at': datetime.now().isoformat()
        }
        videos = load_videos()
        videos.append(video)
        save_videos(videos)
        return redirect(url_for('index'))

    return render_template('upload.html')

@app.route('/pending')
def pending():
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    videos = load_videos()
    unapproved = [v for v in videos if not v.get('approved')]
    return render_template('pending.html', videos=unapproved)

@app.route('/approve/<int:video_id>')
def approve(video_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    videos = load_videos()
    if 0 <= video_id < len(videos):
        videos[video_id]['approved'] = True
        save_videos(videos)
    return redirect(url_for('pending'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = ACCOUNTS.get(username)
        if user and user['password'] == password:
            session['username'] = username
            session['is_admin'] = user['is_admin']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Sai tài khoản hoặc mật khẩu")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
