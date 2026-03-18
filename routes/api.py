from flask import Blueprint, jsonify
from models import Post, User, Category, Reply
from extensions import db

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/stats')
def stats():
    return jsonify({
        'users': User.query.count(),
        'posts': Post.query.filter_by(is_deleted=False).count(),
        'replies': Reply.query.filter_by(is_deleted=False).count(),
        'categories': Category.query.count(),
    })
