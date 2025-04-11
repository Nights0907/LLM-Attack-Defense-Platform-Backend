# -*— coding:utf-8 -*—
from flask import Flask,url_for
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import config

db = SQLAlchemy()
mongo = PyMongo()  # 延迟初始化
bootstrap = Bootstrap()
# login_manager = LoginManager()
# login_manager.session_protection = 'strong'
# login_manager.login_message = '请先登录'
# login_manager.login_view = '/login'

def create_app(config_name):
    # 创建 flask 实例
    app = Flask(__name__)
    # 从配置类中加载配置
    app.config.from_object(config[config_name])
    # 调用配置类中初始化函数，初始化app，这里该初始化函数为空
    config[config_name].init_app(app)

    # 初始化用到的各个模块（关联到当前app）
    bootstrap.init_app(app)
    # db.init_app(app)
    # db.app = app
    # login_manager.init_app(app)

    # 配置 MySQL 连接（格式：mysql+pymysql://用户名:密码@主机/数据库名）
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/llm_attack'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭警告
    db.init_app(app)

    # 配置mongodb
    app.config["MONGO_URI"] = "mongodb://localhost:27017/llm_attack"
    mongo.init_app(app) # initialization

    # 注册蓝图(导入包初始化模块__init__中的内容时，需要加‘.’)
    from .user import user as user_bp
    from .model import model as model_bp
    from .attack import attack as attack_bp
    from .index import index as index_bp
    from .index import logs as logs_bp
    from .index import logging as logging_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(model_bp)
    app.register_blueprint(attack_bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(logging_bp)

    # 返回 flask 实例
    return app






