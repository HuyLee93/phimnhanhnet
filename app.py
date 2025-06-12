from flask import Flask, render_template, request, redirect, url_for, session
from urllib.parse import urlparse, parse_qs
import uuid

app = Flask(__name__)
app.secret_key = 'lekoy93'

videos = []
comments = []
users = {'admin': {'password': 'lekoy93', 'role': 'admin'},
         'guest': {'password': '123', 'role': 'guest'}}


def convert_url_to_embed(url):
    if "youtube.com" in url or "youtu.be" in url:
        if "watch?v=" in url:
            vid_id = parse_qs(urlparse(url).query).get('v', [None])[0]
        elif "youtu.be" in url:
            vid_id = urlparse(url).path.lstrip('/')
        else:
            vid_id = None
        if vid_id:
            return f"https://www.youtube.com/embed/{vid_id}"
    elif "vimeo.com" in url:
        vid_id = urlparse(url).path.lstrip('/')
        return f"https://player.vimeo.com/video/{vid_id}"
    # Mặc định trả về chính URL nếu không xử lý được
    return url


@app.route('/', methods=['GET'])
def index():
    q = request.args.get('q', '')
    category = request.args.get('category', '')
    filtered = [v for v in videos if v['approved']]
    if q:
        filtered = [v for v in filtered if q.lower() in v['title'].lower()]
    if category:
        filtered = [v for v in filtered if v['category'] == category]
    return render_template('index.html', videos=filtered, comments=comments, session=session)


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
        url = convert_url_to_embed(request.form['url'])
        video = {
            'id': str(uuid.uuid4()),
            'title': request.form['title'],
            'url': url,
            'category': request.form['category'],
            'user': session['username'],
            'approved': session['role'] == 'admin'
        }
        videos.append(video)
        return redirect('/')
    return render_template('upload.html')


@app.route('/delete/<id>')
def delete(id):
    if session.get('role') != 'admin':
        return redirect('/')
    global videos
    videos = [v for v in videos if v['id'] != id]
    return redirect('/')


@app.route('/comment/<video_id>', methods=['POST'])
def comment(video_id):
    if 'username' not in session:
        return redirect('/login')
    text = request.form['comment']
    comments.append({'video_id': video_id, 'user': session['username'], 'text': text})
    return redirect('/')


@app.route('/like/<video_id>')
def like(video_id):
    for v in videos:
        if v['id'] == video_id:
            v['likes'] = v.get('likes', 0) + 1
            break
    return redirect('/')


@app.route('/dislike/<video_id>')
def dislike(video_id):
    for v in videos:
        if v['id'] == video_id:
            v['dislikes'] = v.get('dislikes', 0) + 1
            break
    return redirect('/')
