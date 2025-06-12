from flask import Flask, render_template, request, redirect, session, url_for
import re

app = Flask(__name__)
app.secret_key = 'lekoy'

# Dữ liệu tạm
videos = []
users = {'admin': {'password': 'lekoy93', 'role': 'admin'},
         'guest': {'password': '123', 'role': 'guest'}}

# 🔁 Hàm xử lý URL thành iframe nhúng
def convert_url_to_embed(url):
    if '<iframe' in url:
        return url  # đã là iframe, giữ nguyên

    # YouTube dạng youtu.be/abc
    yt_match = re.match(r'https?://youtu\.be/([a-zA-Z0-9_-]+)', url)
    if yt_match:
        code = yt_match.group(1)
        return f'<iframe width="300" height="170" src="https://www.youtube.com/embed/{code}" frameborder="0" allowfullscreen></iframe>'

    # YouTube dạng youtube.com/watch?v=abc
    yt_watch = re.search(r'v=([a-zA-Z0-9_-]+)', url)
    if 'youtube.com' in url and yt_watch:
        code = yt_watch.group(1)
        return f'<iframe width="300" height="170" src="https://www.youtube.com/embed/{code}" frameborder="0" allowfullscreen></iframe>'

    # Facebook, Vimeo... hoặc link iframe không hợp lệ => thông báo lỗi hoặc giữ nguyên
    return url  # fallback (bạn có thể thêm xử lý khác)

# Trang tải lên video
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session or users[session['username']]['role'] != 'admin':
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        raw_url = request.form['url']
        category = request.form['category']
        embed = convert_url_to_embed(raw_url)
        videos.append({'title': title, 'url': embed, 'category': category, 'author': session['username']})
        return redirect('/')
    return render_template('upload.html')
