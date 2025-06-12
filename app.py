from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps

app = Flask(__name__)
app.secret_key = 'lekoy93'

# Admin mặc định
ADMIN_USER = 'admin'
ADMIN_PASS = 'lekoy93'

# Danh sách video (tạm thời trong RAM)
videos = []

# Hàm kiểm tra đăng nhập
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session['username'] != ADMIN_USER:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Trang chính
@app.route('/')
def index():
    search_query = request.args.get('search', '').lower()
    selected_category = request.args.get('category', '')

    filtered_videos = videos
    if search_query:
        filtered_videos = [v for v in filtered_videos if search_query in v['title'].lower()]
    if selected_category:
        filtered_videos = [v for v in filtered_videos if v['category'] == selected_category]

    categories = list(set(v['category'] for v in videos))
    return render_template('index.html', videos=filtered_videos, categories=categories)

# Trang upload
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        title = request.form['title']
        url = request.form['url']
        category = request.form['category']
        videos.append({'title': title, 'url': url, 'category': category})
        return redirect(url_for('index'))
    return render_template('upload.html')

# Trang đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USER and request.form['password'] == ADMIN_PASS:
            session['username'] = ADMIN_USER
            return redirect(url_for('upload'))
    return render_template('login.html')

# Đăng xuất
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

# Khởi chạy
if __name__ == '__main__':
    app.run(debug=True)
