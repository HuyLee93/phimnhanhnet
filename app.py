from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'lekoy_secret'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

videos = []
likes = {}
comments = {}

# Tài khoản admin mặc định
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'lekoy93'

@app.route('/')
def home():
    query = request.args.get('q', '').lower()
    category = request.args.get('category', '')

    filtered = []
    for video in videos:
        if query and query not in video['title'].lower():
            continue
        if category and category != video['category']:
            continue
        filtered.append(video)

    return render_template('index.html', videos=filtered, likes=likes, comments=comments)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('upload'))
        else:
            error = 'Sai tài khoản hoặc mật khẩu'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        url = request.form['url']

        video_file = request.files.get('video')
        video_path = ''
        if video_file and video_file.filename != '':
            filename = secure_filename(video_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            video_file.save(filepath)
            video_path = filepath

        videos.append({
            'title': title,
            'category': category,
            'url': url,
            'file': video_path
        })
        return redirect(url_for('home'))

    return render_template('upload.html')

@app.route('/like/<int:video_id>')
def like(video_id):
    likes[video_id] = likes.get(video_id, 0) + 1
    return redirect(url_for('home'))

@app.route('/comment/<int:video_id>', methods=['POST'])
def comment(video_id):
    content = request.form['comment']
    if video_id not in comments:
        comments[video_id] = []
    comments[video_id].append(content)
    return redirect(url_for('home'))

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
