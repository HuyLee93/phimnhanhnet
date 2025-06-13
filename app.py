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
        return "https://www.youtube.com/embed/" +
