from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import json
import traceback
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'lekoy93'

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATA_FILE = 'data.json'

# Tạo dữ liệu mặc định nếu chưa tồn tại
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({'videos': [], 'users': [
            {'username': 'admin', 'password': 'lekoy93', 'role': 'admin'}
        ]}, f)

# Load dữ liệu
with open(DATA_FILE) as f:
    data = json.load(f)

videos = data.get('videos', [])
users = data.get('users', [])

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump({'videos': videos, 'users': users}, f, indent=4)

def convert_to_embed(url):
    if 'youtube.com/watch?v=' in url:
        video_id = url.split('watch?v=')[1].split('&')[0]
        return f"https://www.youtube.com/embed/{video_id}"
    elif 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[1].split('?')[0]
        return f"https://www.youtube.com/embed/{video_id}"
    elif 'facebook.com/' in url:
        return f"https://www.facebook.com/plugins/video.php?href={url}"
    elif 'vimeo.com/' in url:
        video_id = url.split('/')[-1]
        return f"https://player.vimeo.com/video/{video_id}"
    return url

@app.route('/')
def index():
    keyword = request.args.get('q', '').lower()
    category = request.args.get('category', '')
    filtered = [
        v for v in videos
        if (keyword in v['title'].lower()) and (category in v['category'] if category else True)
    ]
    return render_template('index.html', videos=filtered, user=session.get('user'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        for user in users:
            if user['username'] == username and user['password'] == password:
                session['user'] = user
                return redirect('/')
        error = 'Sai tài khoản hoặc mật khẩu'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            title = request.form.get('title')
            category = request.form.get('category')
            url = request.form.get('url')
            file = request.files.get('file')

            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                url = '/' + filepath
            elif url:
                url = convert_to_embed(url)
            else:
                return "Bạn phải nhập URL hoặc chọn file video.", 400

            videos.append({
                'title': title,
                'category': category,
                'url': url,
                'likes': 0,
                'dislikes': 0,
                'comments': [],
                'uploaded_at': datetime.now().isoformat()
            })
            save_data()
            return redirect('/')

        except Exception as e:
            print("ERROR:", e)
            traceback.print_exc()
            return "Internal Server Error", 500

    return render_template('upload.html', user=session.get('user'))

@app.route('/like/<int:index>')
def like(index):
    if 0 <= index < len(videos):
        videos[index]['likes'] += 1
        save_data()
    return redirect('/')

@app.route('/dislike/<int:index>')
def dislike(index):
    if 0 <= index < len(videos):
        videos[index]['dislikes'] += 1
        save_data()
    return redirect('/')

@app.route('/comment/<int:index>', methods=['POST'])
def comment(index):
    if 0 <= index < len(videos):
        comment_text = request.form.get('comment')
        if comment_text:
            videos[index]['comments'].append(comment_text)
            save_data()
    return redirect('/')

@app.route('/delete/<int:index>')
def delete(index):
    if 'user' in session and session['user']['role'] == 'admin':
        if 0 <= index < len(videos):
            del videos[index]
            save_data()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
