from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import json
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'lekoy93_secret_key'

DATA_FILE = 'videos.json'
COMMENTS_FILE = 'comments.json'
USERS = {'admin': 'lekoy93'}  # Chỉ có admin mới được đăng và xoá video

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def load_videos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_videos(videos):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)

def load_comments():
    if os.path.exists(COMMENTS_FILE):
        with open(COMMENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_comments(comments):
    with open(COMMENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(comments, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    videos = load_videos()
    return render_template('index.html', videos=videos, user=session.get('user'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if USERS.get(username) == password:
            session['user'] = username
            return redirect(url_for('index'))
        else:
            flash('Sai tài khoản hoặc mật khẩu')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        url = request.form['url']
        category = request.form['category']
        video_id = str(uuid.uuid4())
        videos = load_videos()
        videos.append({
            'id': video_id,
            'title': title,
            'url': url,
            'category': category,
            'user': session['user'],
            'approved': session['user'] == 'admin',
            'likes': 0,
            'dislikes': 0
        })
        save_videos(videos)
        flash('Video đã gửi. Admin sẽ duyệt nếu bạn không phải admin.')
        return redirect(url_for('index'))
    return render_template('upload.html', user=session.get('user'))

@app.route('/approve/<id>')
def approve(id):
    if session.get('user') != 'admin':
        return redirect(url_for('index'))
    videos = load_videos()
    for video in videos:
        if video['id'] == id:
            video['approved'] = True
    save_videos(videos)
    return redirect(url_for('admin'))

@app.route('/delete/<id>')
def delete(id):
    if session.get('user') != 'admin':
        return redirect(url_for('index'))
    videos = load_videos()
    videos = [v for v in videos if v['id'] != id]
    save_videos(videos)
    return redirect(url_for('admin'))

@app.route('/admin')
def admin():
    if session.get('user') != 'admin':
        return redirect(url_for('index'))
    videos = load_videos()
    return render_template('admin.html', videos=videos)

@app.route('/video/<id>', methods=['GET', 'POST'])
def video(id):
    videos = load_videos()
    video = next((v for v in videos if v['id'] == id and v['approved']), None)
    if not video:
        return 'Video không tồn tại hoặc chưa được duyệt.'
    comments = load_comments()
    if request.method == 'POST':
        cmt = request.form['comment']
        user = session.get('user', 'Khách')
        comment_obj = {
            'user': user,
            'comment': cmt,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        comments.setdefault(id, []).append(comment_obj)
        save_comments(comments)
    return render_template('video.html', video=video, comments=comments.get(id, []))

@app.route('/like/<id>')
def like(id):
    videos = load_videos()
    for video in videos:
        if video['id'] == id:
            video['likes'] += 1
    save_videos(videos)
    return redirect(url_for('video', id=id))

@app.route('/dislike/<id>')
def dislike(id):
    videos = load_videos()
    for video in videos:
        if video['id'] == id:
            video['dislikes'] += 1
    save_videos(videos)
    return redirect(url_for('video', id=id))

@app.route('/category/<name>')
def category(name):
    videos = load_videos()
    filtered = [v for v in videos if v['category'].lower() == name.lower() and v['approved']]
    return render_template('category.html', videos=filtered, category=name)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
