from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from extensions import db
from models import User, Post, Reply, Category
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_posts': Post.query.filter_by(is_deleted=False).count(),
        'total_replies': Reply.query.filter_by(is_deleted=False).count(),
        'total_categories': Category.query.count(),
        'banned_users': User.query.filter_by(is_banned=True).count(),
        'deleted_posts': Post.query.filter_by(is_deleted=True).count(),
    }
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_posts = Post.query.filter_by(is_deleted=False).order_by(Post.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, recent_users=recent_users, recent_posts=recent_posts)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('q', '').strip()
    query = User.query
    if keyword:
        query = query.filter(User.username.contains(keyword) | User.email.contains(keyword))
    pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', users=pagination.items, pagination=pagination, keyword=keyword)

@admin_bp.route('/users/<int:user_id>/ban', methods=['POST'])
@login_required
@admin_required
def ban_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('不能封禁管理员', 'danger')
        return redirect(url_for('admin.users'))
    user.is_banned = not user.is_banned
    db.session.commit()
    flash(f'用户 {user.username} 已{"封禁" if user.is_banned else "解封"}', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('不能修改自己的权限', 'danger')
        return redirect(url_for('admin.users'))
    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f'用户 {user.username} 已{"设为管理员" if user.is_admin else "取消管理员"}', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/posts')
@login_required
@admin_required
def posts():
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('q', '').strip()
    show_deleted = request.args.get('deleted', 0, type=int)
    query = Post.query
    if not show_deleted:
        query = query.filter_by(is_deleted=False)
    if keyword:
        query = query.filter(Post.title.contains(keyword))
    pagination = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/posts.html', posts=pagination.items, pagination=pagination,
                           keyword=keyword, show_deleted=show_deleted)

@admin_bp.route('/posts/<int:post_id>/pin', methods=['POST'])
@login_required
@admin_required
def pin_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.is_pinned = not post.is_pinned
    db.session.commit()
    flash(f'帖子已{"置顶" if post.is_pinned else "取消置顶"}', 'success')
    return redirect(url_for('admin.posts'))

@admin_bp.route('/posts/<int:post_id>/lock', methods=['POST'])
@login_required
@admin_required
def lock_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.is_locked = not post.is_locked
    db.session.commit()
    flash(f'帖子已{"锁定" if post.is_locked else "解锁"}', 'success')
    return redirect(url_for('admin.posts'))

@admin_bp.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.is_deleted = not post.is_deleted
    db.session.commit()
    flash(f'帖子已{"删除" if post.is_deleted else "恢复"}', 'success')
    return redirect(url_for('admin.posts'))

@admin_bp.route('/categories')
@login_required
@admin_required
def categories():
    cats = Category.query.all()
    return render_template('admin/categories.html', categories=cats)

@admin_bp.route('/categories/add', methods=['POST'])
@login_required
@admin_required
def add_category():
    name = request.form.get('name', '').strip()
    desc = request.form.get('description', '').strip()
    icon = request.form.get('icon', 'fa-folder').strip()
    color = request.form.get('color', '#4f46e5').strip()
    if not name:
        flash('分类名称不能为空', 'danger')
        return redirect(url_for('admin.categories'))
    if Category.query.filter_by(name=name).first():
        flash('分类名称已存在', 'danger')
        return redirect(url_for('admin.categories'))
    cat = Category(name=name, description=desc, icon=icon, color=color)
    db.session.add(cat)
    db.session.commit()
    flash('分类添加成功', 'success')
    return redirect(url_for('admin.categories'))

@admin_bp.route('/categories/<int:cat_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    if cat.post_count > 0:
        flash('该分类下有帖子，无法删除', 'danger')
        return redirect(url_for('admin.categories'))
    db.session.delete(cat)
    db.session.commit()
    flash('分类已删除', 'success')
    return redirect(url_for('admin.categories'))
