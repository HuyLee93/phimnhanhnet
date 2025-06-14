from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import json
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'lekoy_secret_key'
UPLOAD_FOLDER = 'static/videos'
DATA_FILE = 'data/videos.json'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

def load_videos():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_videos(videos):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    videos = load_videos()
    approved_videos = [v for v in videos if v.get('approved', True)]
    return render_template('index.html', videos=approved_videos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'lekoy93':
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            flash('Sai tài khoản hoặc mật khẩu!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        title = request.form['title']
        url = request.form['url']
        category = request.form['category']
        new_video = {
            'id': str(uuid.uuid4()),
            'title': title,
            'url': url,
            'category': category,
            'approved': session.get('admin', False),
            'likes': 0,
            'dislikes': 0,
            'comments': [],
            'upload_time': datetime.now().isoformat()
        }
        videos = load_videos()
        videos.insert(0, new_video)
        save_videos(videos)
        flash('Video đã gửi chờ duyệt!' if not session.get('admin') else 'Đã đăng video!')
        return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    videos = load_videos()
    return render_template('admin.html', videos=videos)

@app.route('/approve/<video_id>')
def approve(video_id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    videos = load_videos()
    for v in videos:
        if v['id'] == video_id:
            v['approved'] = True
            break
    save_videos(videos)
    return redirect(url_for('admin'))

@app.route('/delete/<video_id>')
def delete(video_id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    videos = load_videos()
    videos = [v for v in videos if v['id'] != video_id]
    save_videos(videos)
    return redirect(url_for('admin'))

@app.route('/like/<video_id>')
def like(video_id):
    videos = load_videos()
    for v in videos:
        if v['id'] == video_id:
            v['likes'] += 1
            break
    save_videos(videos)
    return redirect(url_for('index'))

@app.route('/dislike/<video_id>')
def dislike(video_id):
    videos = load_videos()
    for v in videos:
        if v['id'] == video_id:
            v['dislikes'] += 1
            break
    save_videos(videos)
    return redirect(url_for('index'))

@app.route('/comment/<video_id>', methods=['POST'])
def comment(video_id):
    name = request.form['name']
    content = request.form['content']
    videos = load_videos()
    for v in videos:
        if v['id'] == video_id:
            v['comments'].append({
                'name': name,
                'content': content,
                'time': datetime.now().isoformat()
            })
            break
    save_videos(videos)
    return redirect(url_for('index'))

@app.route('/category/<cat>')
def category(cat):
    videos = load_videos()
    filtered = [v for v in videos if v['category'].lower() == cat.lower() and v.get('approved', False)]
    return render_template('category.html', videos=filtered, category=cat)

if __name__ == '__main__':
    app.run()
