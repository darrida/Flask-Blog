from flask import render_template, redirect, url_for, current_app, \
                  flash, request, make_response, abort, jsonify
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from .. import db
from ..models import User, Role, Post, Permission, Comment, postTag, activePost
from ..decorators import admin_required, permission_required
from datetime import datetime



@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query.filter_by(published=True)
    pagination = query.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts,
                           show_followed=show_followed, pagination=pagination)#,
                           #form=form)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('You comment has been published.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
                current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
            page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
            error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)


@main.route('/search', methods=['GET', 'POST'])
def search(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        search_entry = Post.query.title('*' + form.search.data + '*')
        db.session.add(comment)
        db.session.commit()
        flash('You comment has been published.')
        return redirect(url_for('.search_results', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
                current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
            page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
            error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
            page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
            error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE)
def edit(id):
    if id > 0: 
        form = None
        post = Post.query.get_or_404(id)
        post_new = Post(title="", body="", published=0, author=current_user._get_current_object())
        db.session.add(post)
        db.session.flush()
        db.session.refresh(post)
    else:
<<<<<<< HEAD
        new_post = Post(title="", body="", published=0, activePost_id=0, author=current_user._get_current_object())
        db.session.add(new_post)
=======
        post_new = Post(title="", body="", published=0, activePost_id=None, author=current_user._get_current_object())
        db.session.add(post)
>>>>>>> parent of 44c77ec... finished activePosts basics
        db.session.flush()
        db.session.refresh(post)
    if current_user != post.author and id > 0 and not current_user.can(Permission.ADMIN):
            abort(403)   
    if request.method=='POST' and request.form['submit']=='Close':
        flash('The post was not updated.')
        if id > 0:
            return redirect(url_for('.manage_posts'))
        else:
            db.session.rollback()
            return redirect(url_for('.manage_posts'))
    elif request.method=='POST' and current_user.can(Permission.WRITE):
        if request.form['title'] == "" and request.form['body'] == "":
            flash('Title and Body required')
            return redirect(url_for('.edit', id=0))
        else:
            post_new.title=request.form['title']
            post_new.body=request.form['body']
            post_new.published=(0 if request.form['submit']=='Save Draft' else 1)
            if post.activePost_id is not None:
                post_new.activePost_id = post.activePost_id
            db.session.add(post_new)
            db.session.flush()
            db.session.refresh(post_new)
            db.session.commit()
            if request.form['submit']=='Save Draft':
                flash('The post has been updated as a draft.')
                return redirect(url_for('.edit', id=post_new.id))
            else:
                flash('The post has been updated and published.')
            if request.form['submit']=='Publish':
                return redirect(url_for('.post', id=post_new.id))
    form = PostForm()
    form.title.data = post.title
    form.body.data = post.body
    form.id.data = post.id
    if id > 0:
        if post.published == 1:
            form.status.data = 'Published'
        elif post.published == 0:
            form.status.data = 'Saved Draft'
    else:
        form.status.data = 'Not Saved'
    action = ('Edit' if id > 0 else 'Create')
    return render_template('edit_post.html', action=action, form=form)


@main.route('/edit2/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE)
def edit2(id):
    if id > 0: 
        form = None
        #post = Post.query.get_or_404(id)
        active_post = activePost.query.get_or_404(id)
        post = Post.query.filter_by(id=active_post.post_id).first()
        #post.activePost_id = post.activePost_id + 1
        new_post = Post(title=post.title, 
                        body=post.body,
                        published=post.published,
                        activePost_id = post.activePost_id + 1,
                        author=post.author)
        #db.session.add(new_post)
        #db.session.flush()
        #db.session.refresh(new_post)
    else:
        new_post = Post(title="", body="", published=0, activePost_id=0, author=current_user._get_current_object())
        #db.session.add(new_post)
        ##db.session.flush()
        #db.session.refresh(new_post)
    if id > 0:
        if current_user != post.author or not current_user.can(Permission.ADMIN):
            abort(403)   
    if request.method=='POST' and request.form['submit']=='Close':
        flash('The post was not updated.')
        if id > 0:
            return redirect(url_for('.manage_posts'))
        else:
            db.session.rollback()
            return redirect(url_for('.manage_posts'))
    elif request.method=='POST' and current_user.can(Permission.WRITE):
        if request.form['title'] == "" and request.form['body'] == "":
            flash('Title and Body required')
            return redirect(url_for('.edit2', id=0))
        elif request.form['post_type'] == 'quicksave':
            flash('quick save weirdness')
        else:
            new_post.title = request.form['title']
            new_post.body = request.form['body']
            new_post.published = (0 if request.form['submit'] == 'Save Draft' else 1)
            if request.form['post_type'] == 'edit':
                new_post.activePost_id = post.activePost_id
            else:
                new_post.activePost_id = 0
            db.session.add(new_post)
            db.session.flush()
            db.session.refresh(new_post)
            db.session.commit()
            active_post = activePost.query.get_or_404(new_post.activePost_id)
            if request.form['submit'] == 'Save Draft':
                flash('The post has been updated as a draft.')
                return redirect(url_for('.edit2', id=active_post.id))
            else:
                flash(str(new_post.activePost_id))
                flash(str(request.form['post_type']))
                flash('The post has been updated and published.')
            if request.form['submit'] == 'Publish':
                return redirect(url_for('.edit2', id=active_post.id))
    form = PostForm()
    #form.title.data = post.title
    #form.body.data = post.body
    #form.id.data = post.id
    if id > 0:
        form.title.data = post.title
        form.body.data = post.body
        #form.id.data = post.id
        form.post_type.data = 'edit'
        if post.published == 1:
            form.status.data = 'Published'
        elif post.published == 0:
            form.status.data = 'Saved Draft'
    else:
        form.title.data = new_post.title
        form.body.data = new_post.body
        #form.id.data = new_post.id
        form.post_type.data = 'new'
        form.status.data = 'Not Saved'
    flash('post id: ' + str(post.id))
    flash('active id: ' + str(post.activePost_id))
    action = ('Edit' if id > 0 else 'Create')
    return render_template('edit_post.html', action=action, form=form)



@main.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)


@main.route('/_quick_save')
@login_required
@permission_required(Permission.WRITE)
def quick_save():
    post_id=request.args.get('post_id', 0, type=int)
    post = Post.query.get_or_404(post_id)
    post.published=(False if request.args.get('post_status', 0, type=str)=='Saved Draft' else True)
    post.title=request.args.get('post_title', 0, type=str)
    post.body=request.args.get('post_body', 0, type=str)
    db.session.add(post)
    db.session.commit()
    return jsonify(result="Last save: " + str(datetime.now().strftime("%I:%M:%S")))
    


@main.route('/manage', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE)
def manage_posts():
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = False#bool(request.cookies.get('show_followed', ''))
    query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
    posts = pagination.items
    return render_template('manage_posts.html', posts=posts,
                           show_followed=show_followed, pagination=pagination)#,
                           #form=form)

    
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    #role_choices = [(roles.id, roles.name)
    #                         for roles in Role.query.order_by(Role.name).all()]
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    #form.role.choices = role_choices
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
            page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
            error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)  # 30 days
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)  # 30 days
    return resp

@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'