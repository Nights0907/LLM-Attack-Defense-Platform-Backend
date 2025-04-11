# -*— coding:utf-8 -*—
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db


class AttackParameter(db.Model):
    __tablename__ = 'attack_records'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    # 主键字段
    id = db.Column(db.String(80), primary_key=True, unique=True)
    # 时间字段（可为空）
    time = db.Column(db.DateTime)
    # 用户名字段（可为空）
    username = db.Column(db.String(80), index=True)
    # 攻击方法字段（非空）
    attack_method = db.Column(db.String(80), nullable=False, index=True)
    # 有害问题集路径字段
    malicious_question_set = db.Column(db.String(80),index=True)
    # 目标模型名字段（非空）
    attack_model = db.Column(db.String(80), nullable=False, index=True)
    # 重试次数字段（非空）
    retry_times = db.Column(db.Integer, nullable=True, default=10)
    # prompt 加载默认问题
    prompt = db.Column(db.String(80), index=True)

# 定义数据模型（ORM）
class user_info(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), unique=True, nullable=False)
    is_login = db.Column(db.SmallInteger, default=0, nullable=False)  # 使用 TINYINT

class model_info(db.Model):
    model_id = db.Column(db.Integer, primary_key=True)
    base_url= db.Column(db.String(255), unique=True, nullable=False)
    model_name = db.Column(db.String(255), unique=True, nullable=False)
    api_key = db.Column(db.String(255), unique=True, nullable=False)





