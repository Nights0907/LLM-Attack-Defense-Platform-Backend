# -*— coding:utf-8 -*—
import json
import re
import time

# flask框架 所需包
from flask import render_template, Response, request, jsonify

from . import user
from .. import db
from ..models import user_info

@user.route('/api/users/login', methods=['GET', 'POST'])
def login():
    # 查询所有用户
    data = request.get_json()
    username = data["username"]
    password = data["password"]

    curr_user = user_info.query.filter_by(username=username).first()

    if curr_user.password == password:
        # 手动构建字典
        user_data = {
            'uid': curr_user.uid,
            'username': curr_user.username,
            'password': curr_user.password,
            'is_login': 1
        }
        return jsonify(user_data)
    else:
        return "password incorrect!"


@user.route('/api/users/register', methods=['POST'])
def register():
    # 获取 JSON 数据
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # 检查必要字段
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # 检查用户名是否已存在
    if user_info.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409

    try:
        # 创建新用户
        # 生成用户ID
        uid = re.sub(r'\D', '', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        new_user = user_info(uid = uid ,username=username, password=password,is_login=0)

        # 添加到数据库
        db.session.add(new_user)
        db.session.commit()

        # 返回注册成功的用户信息（类似你的登录返回格式）
        user_data = {
            'uid': new_user.uid,
            'username': new_user.username,
            'password' : new_user.password,
            'is_login': 1  # 注册后直接视为登录
        }
        return jsonify(user_data)

    except Exception as e:
        db.session.rollback()  # 出错时回滚
        return jsonify({"error": "Registration failed", "details": str(e)})