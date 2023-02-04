import os
from flask import Blueprint, render_template, abort, current_app, request, flash, url_for, redirect, send_from_directory, session
from jinja2 import TemplateNotFound
from utils.utils import send_simple_message
from wtforms import Form, TextAreaField, validators, StringField
from .models import Blog, db
import datetime
from flask_login import login_required, current_user
from tempfile import NamedTemporaryFile



APP_PATH = os.path.dirname(os.path.realpath(__file__))
PAGE_DIR = os.path.join(APP_PATH, 'pages')
BLOG_IMG_DIR = os.path.join(APP_PATH, 'static/blog')
BLOG_TMPLT_DIR = os.path.join(APP_PATH, 'templates/blog')

blog_bp = Blueprint('blog_bp', __name__)


@blog_bp.route('/blog', methods=['GET'])
def blog():
    blog_posts = Blog.query.order_by(Blog.created_at.desc()).all()
    return render_template('blog.html', title='Blog', blog_posts=blog_posts)

@blog_bp.route('/blog/<path>', methods=['GET'])
def blog_read_more(path):
    title = Blog.query.get(path)
    blog_dir = 'blog/'+ title.title + '/' + title.title
    return render_template(f'{blog_dir}.html', title=title)

@blog_bp.route('/blog/write', methods=['GET', 'POST'])
@login_required
def blog_write():
    if not current_user.is_admin():
        return redirect('/blog')
    if request.method == 'POST':
        title = request.form.get('title')
        html = request.form.get('html')
        text = request.form.get('text')
        text = text[:300]
        if title == 'Title':
            return redirect('/')
        start_html = "{% extends 'base.html' %} {% set active_page = 'blog' %} {% block content %}"
        end_html = "{% endblock %}"
        title = title.rstrip()
        title = title.replace(' ','-')
        dir_img_path = os.path.join(BLOG_IMG_DIR, title)
        dir_tmplt_path = os.path.join(BLOG_TMPLT_DIR, title)
        if not os.path.exists(dir_img_path):
            os.makedirs(dir_img_path)
            os.makedirs(dir_tmplt_path)
        try:
            for key in request.files:
                image = request.files.get(key)
                image.save(dir_img_path+'/'+image.filename)
            with open(dir_tmplt_path + '/' + f'{title}.html', 'w') as file:
                file.write(start_html + html + end_html)
        except:
            pass
        db_entry = Blog(
            title = title,
            text = text
        )
        db.session.add(db_entry)
        db.session.commit()
        flash('Blog entry submitted.', category='success')
        return render_template('blog-write.html', title='Blog')
            
    return render_template('blog-write.html', title='Blog')

