from flask import Flask, render_template, request, redirect, session, url_for
from datetime import datetime
import re

app = Flask(__name__)
app.secret_key = "lekoy_secret_key"

videos = []
admin_user = {'username': 'admin', 'password': 'lekoy93', 'role': 'admin'}

def convert_to_embed(url):
    # Tự động chuyển link thành iframe nhúng
    if "youtube.com/watch?v=" in url:
        return url.replace("watch?v=", "embed/")
    elif "youtu.be/" in url:
        return "https://www.youtube.com/embed/def convert_url_to_embed(url):
    if "youtube.com" in url or "youtu.be" in url:
        import re
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
        if match:
            video_id = match.group(1)
            return "https://www.youtube.com/embed/" + video_id
    elif "facebook.com" in url:
        return f"https://www.facebook.com/plugins/video.php?href={url}"
    elif "vimeo.com" in url:
        return url.replace("vimeo.com", "player.vimeo.com/video")
    else:
        return url  # fallback: dùng nguyên URL
" + video_id

