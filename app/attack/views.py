# -*— coding:utf-8 -*—

# flask框架 所需包
from flask import render_template,request,session,redirect,url_for,abort,flash,json,jsonify
from flask_login import login_required,current_user,login_user,logout_user

# LLM attack 所需包
from . import attack
from .deepinception.deepinception import deep_inception
from .jailbreakingllm.jailbreakingllm import jailbreakingllm
from .renellm.renellm import renellm
from .codechameleon.codechameleon import codechameleon
from .sap.attack import sap

# flask 数据库 所需包
import os
from app import db
from app.models import AttackParameter
from sqlalchemy import or_,and_
from datetime import datetime


# 获取 目标大模型 黑盒攻击结果
@attack.route('/api/attack',methods=['GET','POST'])
# @login_required 暂时不需要用户登录
def attack():
    # 获取前端发送的JSON数据
    data = request.get_json()

    # 验证必要字段是否存在 : (username 用户名 || attack_method 攻击方法 || attack_model 目标模型 || malicious_question_set 有害问题数据集)
    required_fields = ['username','attack_method','attack_model',"malicious_question_set"]
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # 获取系统时间,生成用户登录ID
    formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    username = data['username']
    id = username+'_'+formatted_time

    # 根据攻击方法获得对应有害数据集
    if data['attack_method'] == "renellm" and data["malicious_question_set"] == "advbench" :
        malicious_question_set = "app/data/renellm/advbench/harmful_behaviors_test.csv"
    elif data['attack_method'] == "codechameleon" and data["malicious_question_set"] == "advbench" :
        malicious_question_set = "app/data/codechameleon/all_problem_test.csv"
    elif data['attack_method'] == "deepinception" and data["malicious_question_set"] == "advbench" :
        malicious_question_set = "app/data/deepinception/data"
    elif data['attack_method'] == "jailbreakingllm" and data["malicious_question_set"] == "advbench" :
        malicious_question_set = "app/data/jailbreakingllm/all_problem_test.csv"
    elif data['attack_method'] == "sap" and data["malicious_question_set"] == "advbench" :
        malicious_question_set = "app/data/sap/all_problem_test.csv"


    # 创建AttackRecord对象并赋值
    attack_parameter = AttackParameter(
        id=id,
        time=formatted_time,
        username=username,
        attack_method=data['attack_method'],
        malicious_question_set=malicious_question_set,
        attack_model=data['attack_model'],
        retry_times=10
    )

    # 这里可以添加数据库保存操作
    # db.session.add(attack_parameter)
    # db.session.commit()

    # 处理后端逻辑,目前可以选择五种攻击方法
    if data["attack_method"] == "renellm" :
        result = renellm(attack_parameter)
    elif  data["attack_method"] == "codechameleon" :
        result = codechameleon(attack_parameter)
    elif data["attack_method"] == "deepinception" :
        result = deep_inception(attack_parameter)
    elif data["attack_method"] == "jailbreakingllm":
        result = jailbreakingllm(attack_parameter)
    elif data["attack_method"] == "sap":
        result = sap(attack_parameter)

    return jsonify(result)

