from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'lekoy93'

# Dữ liệu tạm
videos = []
users = {'admin': {'password': 'lekoy93', 'role': 'admin'}}
pending_videos = []

# -------------------- ROUTES ---------------------

@app.route('/')
def index():
    keyword = request.args.get('q', '').lower()
    category = request.args.get('category', '')

    filtered = [v for v in videos if
                (keyword in v['title'].lower()) and
                (category == '' or v['category'] == category)]
    return render_template('index.html', videos=filtered, session=session)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        if u in users and users[u]['password'] == p:
            session['username'] = u
            session['role'] = users[u]['role']
            return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        new_video = {
            'id': str(uuid.uuid4()),
            'title': request.form['title'],
            'url': request.form['url'],
            'category': request.form['category'],
            'author': session['username'],
            'likes': 0,
            'comments': [],
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        if session['role'] == 'admin':
            videos.append(new_video)
        else:
            pending_videos.append(new_video)
        return redirect('/')
    return render_template('upload.html')

@app.route('/approve/<video_id>')
def approve(video_id):
    if session.get('role') == 'admin':
        for v in pending_videos:
            if v['id'] == video_id:
                videos.append(v)
                pending_videos.remove(v)
                break
    return redirect('/')

@app.route('/delete/<video_id>')
def delete(video_id):
    if session.get('role') == 'admin':
        global videos
        videos = [v for v in videos if v['id'] != video_id]
    return redirect('/')

@app.route('/comment/<video_id>', methods=['POST'])
def comment(video_id):
    text = request.form['comment']
    for v in videos:
        if v['id'] == video_id:
            v['comments'].append({'author': session.get('username', 'guest'), 'text': text})
            break
    return redirect('/')

@app.route('/like/<video_id>')
def like(video_id):
    for v in videos:
        if v['id'] == video_id:
            v['likes'] += 1
            break
    return redirect('/')
