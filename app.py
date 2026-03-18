from flask import Flask
from extensions import db, login_manager
from models import User
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'forum-secret-key-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forum.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.admin import admin_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('errors/404.html'), 404

    with app.app_context():
        db.create_all()
        seed_data()

    return app

def seed_data():
    from models import User, Category, Post, Reply
    from werkzeug.security import generate_password_hash
    from datetime import datetime, timedelta
    import random

    if User.query.first():
        return

    # 创建管理员
    admin = User(
        username='admin',
        email='admin@forum.com',
        password_hash=generate_password_hash('admin123'),
        is_admin=True,
        avatar='https://api.dicebear.com/7.x/avataaars/svg?seed=admin',
        bio='论坛管理员',
        created_at=datetime.utcnow()
    )
    db.session.add(admin)

    # 创建示例用户
    users = []
    names = ['张三', '李四', '王五', '赵六', '孙七']
    for i, name in enumerate(names):
        u = User(
            username=name,
            email=f'user{i+1}@forum.com',
            password_hash=generate_password_hash('123456'),
            avatar=f'https://api.dicebear.com/7.x/avataaars/svg?seed={name}',
            bio=f'我是{name}，论坛普通用户',
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
        )
        users.append(u)
        db.session.add(u)

    db.session.flush()

    # 创建分类
    categories_data = [
        ('综合讨论', 'fa-comments', '#4f46e5', '什么都可以聊'),
        ('技术交流', 'fa-code', '#0891b2', '编程、技术、开发'),
        ('生活随笔', 'fa-heart', '#e11d48', '生活感悟、日常分享'),
        ('问答求助', 'fa-question-circle', '#d97706', '有问必答'),
        ('资源分享', 'fa-share-alt', '#16a34a', '好东西一起分享'),
    ]
    categories = []
    for name, icon, color, desc in categories_data:
        c = Category(name=name, icon=icon, color=color, description=desc)
        categories.append(c)
        db.session.add(c)

    db.session.flush()

    # 创建示例帖子
    posts_data = [
        ('欢迎来到WorkForum论坛！', '这里是大家交流的地方，欢迎分享你的想法和经验！论坛规则：友善交流，禁止广告，尊重他人。', 0),
        ('Python Flask 入门教程分享', 'Flask是一个轻量级的Python Web框架，非常适合初学者和小型项目。今天分享一些入门资源...', 1),
        ('今天天气真好，分享一首诗', '春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。生活需要一点诗意~', 2),
        ('求助：如何优化SQL查询速度？', '最近项目遇到数据库查询慢的问题，表里有100万条数据，每次查询都需要5秒以上，请问如何优化？', 3),
        ('分享：免费学习资源大合集', 'Coursera、edX、MIT OpenCourseWare、B站等平台都有大量免费课程，整理了一份清单...', 4),
        ('Vue 3 + TypeScript 最佳实践', '用了半年Vue3，总结了一些实践经验，包括组合式API、状态管理、性能优化等方面...', 1),
        ('读书笔记：《人类简史》', '这本书从宇宙大爆炸讲到21世纪，视角宏大，让人对人类的存在有了全新的认识...', 2),
        ('Docker 部署 Flask 应用完整指南', '记录了从零开始用Docker部署Flask应用的全过程，包括Dockerfile编写、docker-compose配置...', 1),
    ]

    all_users = [admin] + users
    for i, (title, content, cat_idx) in enumerate(posts_data):
        author = all_users[i % len(all_users)]
        p = Post(
            title=title,
            content=content,
            author_id=author.id,
            category_id=categories[cat_idx].id,
            views=random.randint(50, 500),
            is_pinned=(i == 0),
            created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 72))
        )
        db.session.add(p)

    db.session.flush()

    # 创建示例回复
    posts = Post.query.all()
    reply_texts = [
        '非常有帮助，感谢分享！',
        '学到了很多，期待更多内容',
        '这个问题我也遇到过，可以试试加索引',
        '写得很好，收藏了！',
        '支持一下，希望论坛越来越好',
        '请问有相关的参考资料吗？',
    ]
    for post in posts[:5]:
        for j in range(random.randint(1, 4)):
            r = Reply(
                content=random.choice(reply_texts),
                author_id=random.choice(all_users).id,
                post_id=post.id,
                created_at=datetime.utcnow() - timedelta(minutes=random.randint(10, 300))
            )
            db.session.add(r)

    db.session.commit()
    print("[OK] Sample data initialized")

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
