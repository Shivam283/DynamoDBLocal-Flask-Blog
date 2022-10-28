import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from .auth import login_required
from .db import get_posts_db, createPost, postDelete, updatePost, getPost
from .config import UPLOAD_FOLDER
from .entities import User, Post

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    posts = get_posts_db()
    return render_template('blog/index.html', posts=posts)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        if not title:
            error = 'Title is required.'

        file = None
        if request.files['image'].filename != '':
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
            else:
                error = "Wrong File Type for image"

        if error is not None:
            flash(error)
        else:
            if file:
                resp = createPost(title, body, g.user.username, filename)
            else:
                resp = createPost(title, body, g.user.username)
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(userpost, time):

    if userpost == g.user.username:
        return getPost(userpost, time)

    if userpost is None:
        abort(404, f"Post doesn't exist.")

    if userpost != g.user.username:
        abort(403)



@bp.route('/update/<string:user>/<string:time>', methods=('GET', 'POST'))
@login_required
def update(user, time):
    post = get_post(user, time)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        file = ''
        if request.files['image'].filename != '':
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
            else:
                error = "Wrong File Type for image"

        if error is not None:
            flash(error)
        else:
            if file != '':
                upd = updatePost(user, time, title, body, filename)
            else:
                upd = updatePost(user, time, title, body)
            
            return redirect(url_for('blog.index'))
        
    return render_template('blog/update.html', post=post)

@bp.route('/delete/<string:user>/<string:time>', methods=('POST',))
@login_required
def delete(user, time):
    post = get_post(user, time)
    postDelete(user, time)
    return redirect(url_for('blog.index'))