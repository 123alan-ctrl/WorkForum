from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            if user.is_banned:
                flash('您的账号已被封禁，请联系管理员', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        flash('用户名或密码错误', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        if not username or not email or not password:
            flash('请填写所有必填项', 'danger')
            return render_template('auth/register.html')
        if password != confirm:
            flash('两次密码不一致', 'danger')
            return render_template('auth/register.html')
        if len(password) < 6:
            flash('密码至少需要6位', 'danger')
            return render_template('auth/register.html')
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'danger')
            return render_template('auth/register.html')
        if User.query.filter_by(email=email).first():
            flash('邮箱已注册', 'danger')
            return render_template('auth/register.html')
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            avatar=f'https://api.dicebear.com/7.x/avataaars/svg?seed={username}'
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('注册成功，欢迎加入！', 'success')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('main.index'))
