from datetime import datetime

from flask import current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.main import bp
from app.main.forms import EditProfileForm, PostForm
from app.models import User, Post, PostVersion


def pagination(endpoint, request, post_query, user=None):
    username = user.username if user is not None else None
    page = request.args.get('page', 1, type=int)
    posts = post_query.order_by(Post.timestamp.desc()).paginate(
            page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for(
        endpoint, username=username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for(
        endpoint, username=username, page=posts.prev_num) \
        if posts.has_prev else None
    return next_url, prev_url, posts


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is here!')
        return redirect(url_for('main.index'))
    post_query = current_user.followed_posts()
    next_url, prev_url, posts = pagination(
        'main.index', request, post_query)
    return render_template('index.html', title='Home',
                            form=form, posts=posts.items,
                            next_url=next_url, prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    post_query = Post.query
    next_url, prev_url, posts = pagination(
        'main.explore', request, post_query)
    return render_template('index.html', title='Explore',
                            posts=posts.items, next_url=next_url,
                            prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    post_query = user.posts
    next_url, prev_url, posts = pagination(
        'user', request, post_query, user)
    return render_template('user.html', user=user, posts=posts.items,
                            next_url=next_url, prev_url=prev_url)


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes has been saved')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',
                            title='Edit Profile',
                            form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are now following {username}')
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You are not following {username}')
    return redirect(url_for('main.user', username=username))


@bp.route('/delete_post/<id>')
@login_required
def delete_post(id):
    post = Post.query.filter_by(
        user_id=current_user.id, id=int(id)).first_or_404()
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for(
        'main.user', username=current_user.username))


@bp.route('/post/<id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.filter_by(
        user_id=current_user.id, id=int(id)).first_or_404()
    form = PostForm()
    if form.validate_on_submit():
        edited_post = PostVersion(body=post.body, original=post)
        db.session.add(edited_post)
        post.body = form.post.data
        db.session.commit()
        return redirect(url_for(
            'main.user', username=current_user.username))
    elif request.method == 'GET':
        form.post.data = post.body
    return render_template('post_edit.html', title='Edit Post',
                            form=form, post=post)


@bp.route('/history/<id>')
@login_required
def history(id):
    versions = PostVersion.query.filter_by(
        post_id=int(id)).order_by(PostVersion.timestamp.desc())
    return jsonify(versions=[v.serialize() for v in versions])


