from flask import Flask, render_template, request, redirect, session
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'lekoy93'

# Giả lập cơ sở dữ liệu
videos = []
users = {
    'admin': {'password': 'lekoy93', 'role': 'admin'},
    'guest': {'password': 'guest', 'role': 'guest'}
}

@app.route('/')
def index():
    q = request.args.get('q', '').lower()
    category = request.args.get('category', '')
    filtered = [v for v in videos if
                (q in v['title'].lower()) and
                (category == '' or v['category'] == category) and
                v.get('approved', True)]
    return render_template('index.html', videos=filtered, category=category, q=q)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        if u in users and users[u]['password'] == p:
            session['username'] = u
            return redirect('/')
        else:
            error = 'Sai tài khoản hoặc mật khẩu'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect('/login')
    role = users[session['username']]['role']
    if request.method == 'POST':
        v = {
            'id': str(uuid.uuid4()),
            'title': request.form['title'],
            'url': request.form['url'],
            'category': request.form['category'],
            'user': session['username'],
            'approved': role == 'admin',
            'likes': 0,
            'dislikes': 0,
            'comments': []
        }
        videos.append(v)
        return redirect('/')
    return render_template('upload.html')

@app.route('/delete/<id>')
def delete(id):
    if 'username' not in session or users[session['username']]['role'] != 'admin':
        return redirect('/login')
    global videos
    videos = [v for v in videos if v['id'] != id]
    return redirect('/')

@app.route('/like/<id>')
def like(id):
    for v in videos:
        if v['id'] == id:
            v['likes'] += 1
            break
    return redirect('/')

@app.route('/dislike/<id>')
def dislike(id):
    for v in videos:
        if v['id'] == id:
            v['dislikes'] += 1
            break
    return redirect('/')

@app.route('/comment/<id>', methods=['POST'])
def comment(id):
    text = request.form['comment']
    user = session.get('username', 'Khách')
    for v in videos:
        if v['id'] == id:
            v['comments'].append({'user': user, 'text': text})
            break
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
