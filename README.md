# WorkForum 论坛

一个基于 **Flask + SQLite** 构建的功能完整的论坛系统，包含首页、用户页面和管理员页面。

## 功能特性

### 首页
- 帖子列表（分页显示）
- 分类导航栏（按分类筛选）
- 关键词搜索
- 置顶帖子高亮显示
- 热门帖子侧边栏
- 论坛数据统计

### 用户功能
- 注册 / 登录 / 退出
- 发布帖子（选择分类）
- 回复帖子
- 个人主页（查看发帖记录）
- 个人设置（修改邮箱、简介、密码）

### 管理员功能
- 数据统计控制台
- 用户管理（封禁 / 解封 / 设置管理员）
- 帖子管理（置顶 / 锁定 / 删除 / 恢复）
- 分类管理（添加 / 删除分类）

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Flask 3.x |
| 数据库 | SQLite（via Flask-SQLAlchemy） |
| 用户认证 | Flask-Login |
| 密码加密 | Werkzeug |
| 前端 | Jinja2 模板 + 原生 CSS/JS |
| 图标 | Font Awesome 6 |
| 头像 | DiceBear API |

## 快速开始

### 环境要求
- Python 3.8+

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/<your-username>/WorkForum.git
cd WorkForum

# 2. 创建虚拟环境（推荐）
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动应用（自动初始化数据库和示例数据）
python app.py
```

访问 [http://127.0.0.1:5000](http://127.0.0.1:5000) 即可使用。

## 演示账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | `admin` | `admin123` |
| 普通用户 | `张三` | `123456` |
| 普通用户 | `李四` | `123456` |

> 首次启动时会自动创建示例数据（用户、分类、帖子、回复）。

## 项目结构

```
WorkForum/
├── app.py              # Flask 主应用 & 数据初始化
├── extensions.py       # Flask 扩展初始化
├── models.py           # 数据库模型（User/Category/Post/Reply）
├── requirements.txt    # 依赖列表
├── routes/
│   ├── auth.py         # 认证路由（登录/注册/退出）
│   ├── main.py         # 主路由（首页/帖子/用户）
│   ├── admin.py        # 管理员路由
│   └── api.py          # API 路由
└── templates/
    ├── base.html       # 基础模板（导航栏/样式）
    ├── auth/           # 登录 & 注册页
    ├── main/           # 首页 & 帖子详情 & 发帖
    ├── user/           # 用户主页 & 设置
    ├── admin/          # 管理后台（控制台/用户/帖子/分类）
    └── errors/         # 错误页（403/404）
```

## 截图预览

| 首页 | 管理后台 |
|------|----------|
| 帖子列表、分类导航、搜索框 | 数据统计、用户/帖子/分类管理 |

## License

MIT License
