from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from extensions import db
from models import Post, Reply, Category, User
from datetime import datetime
from sqlalchemy import or_

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    cat_id = request.args.get('cat', 0, type=int)
    keyword = request.args.get('q', '').strip()

    query = Post.query.filter_by(is_deleted=False)
    if cat_id:
        query = query.filter_by(category_id=cat_id)
    if keyword:
        query = query.filter(or_(Post.title.contains(keyword), Post.content.contains(keyword)))

    pinned = query.filter_by(is_pinned=True).order_by(Post.created_at.desc()).all() if not keyword else []
    normal_query = query.filter_by(is_pinned=False) if not keyword else query
    pagination = normal_query.order_by(Post.created_at.desc()).paginate(page=page, per_page=15, error_out=False)

    categories = Category.query.all()
    hot_posts = Post.query.filter_by(is_deleted=False).order_by(Post.views.desc()).limit(5).all()
    stats = {
        'users': User.query.count(),
        'posts': Post.query.filter_by(is_deleted=False).count(),
        'replies': Reply.query.filter_by(is_deleted=False).count(),
    }
    return render_template('main/index.html',
                           posts=pagination.items,
                           pinned=pinned,
                           pagination=pagination,
                           categories=categories,
                           hot_posts=hot_posts,
                           stats=stats,
                           current_cat=cat_id,
                           keyword=keyword)

@main_bp.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.filter_by(id=post_id, is_deleted=False).first_or_404()
    post.views += 1
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    replies_pagination = Reply.query.filter_by(post_id=post_id, is_deleted=False)\
        .order_by(Reply.created_at.asc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('main/post_detail.html', post=post, replies=replies_pagination)

@main_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    categories = Category.query.all()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        cat_id = request.form.get('category_id', type=int)
        if not title or not content or not cat_id:
            flash('请填写完整内容', 'danger')
            return render_template('main/new_post.html', categories=categories)
        post = Post(title=title, content=content, author_id=current_user.id, category_id=cat_id)
        db.session.add(post)
        db.session.commit()
        flash('发帖成功！', 'success')
        return redirect(url_for('main.post_detail', post_id=post.id))
    return render_template('main/new_post.html', categories=categories)

@main_bp.route('/post/<int:post_id>/reply', methods=['POST'])
@login_required
def reply_post(post_id):
    post = Post.query.filter_by(id=post_id, is_deleted=False).first_or_404()
    if post.is_locked:
        flash('该帖子已锁定，不能回复', 'warning')
        return redirect(url_for('main.post_detail', post_id=post_id))
    content = request.form.get('content', '').strip()
    if not content:
        flash('回复内容不能为空', 'danger')
        return redirect(url_for('main.post_detail', post_id=post_id))
    reply = Reply(content=content, author_id=current_user.id, post_id=post_id)
    db.session.add(reply)
    db.session.commit()
    flash('回复成功！', 'success')
    return redirect(url_for('main.post_detail', post_id=post_id) + f'#reply-{reply.id}')

@main_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author_id != current_user.id and not current_user.is_admin:
        abort(403)
    post.is_deleted = True
    db.session.commit()
    flash('帖子已删除', 'success')
    return redirect(url_for('main.index'))

@main_bp.route('/user/<int:user_id>')
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author_id=user_id, is_deleted=False)\
        .order_by(Post.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('user/profile.html', profile_user=user, posts=posts)

@main_bp.route('/user/settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    if request.method == 'POST':
        bio = request.form.get('bio', '').strip()
        email = request.form.get('email', '').strip()
        new_password = request.form.get('new_password', '')
        current_password = request.form.get('current_password', '')
        from werkzeug.security import check_password_hash, generate_password_hash
        if not check_password_hash(current_user.password_hash, current_password):
            flash('当前密码错误', 'danger')
            return render_template('user/settings.html')
        if email != current_user.email:
            if User.query.filter_by(email=email).first():
                flash('邮箱已被使用', 'danger')
                return render_template('user/settings.html')
            current_user.email = email
        current_user.bio = bio
        if new_password:
            if len(new_password) < 6:
                flash('新密码至少6位', 'danger')
                return render_template('user/settings.html')
            current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash('设置已保存', 'success')
    return render_template('user/settings.html')
