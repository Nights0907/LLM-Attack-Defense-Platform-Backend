from flask import request

from . import defense
from .. import db
from ..models import defense_method_info


@defense.route('/api/defense',methods=['POST'])
# @login_required 暂时不需要用户登录
def add_attack_method():
    data = request.get_json()
    defense_method_name = data["defense_method_name"]
    defense_method_prompt = data["defense_method_prompt"]

    # 获取攻击方法 id
    defense_method_id = str(len(defense_method_info.query.all())+1).zfill(3)

    new_method = defense_method_info(
        defense_method_id = defense_method_id,
        defense_method_name = defense_method_name,
        defense_method_prompt = defense_method_prompt
    )

    # 返回数据
    defense_method = {}
    defense_method["defense_method_id"] = defense_method_id
    defense_method["defense_method_name"] = defense_method_name
    defense_method["defense_method_prompt"] = defense_method_prompt

    # 插入数据库
    db.session.add(new_method)
    db.session.commit()
    db.session.close()

    return defense_method


@defense.route('/api/defense',methods=['PUT'])
# @login_required 暂时不需要用户登录
def modify_defense_method():
    data = request.get_json()
    old_defense_method_name = data["old_defense_method_name"]
    new_defense_method_name = data["new_defense_method_name"]
    new_defense_method_prompt = data["new_defense_method_prompt"]

    old_defense_method = defense_method_info.query.filter_by(defense_method_name = old_defense_method_name).first()
    old_defense_method.defense_method_name = new_defense_method_name
    old_defense_method.defense_method_prompt = new_defense_method_prompt

    # 返回数据
    defense_method = {}
    defense_method["defense_method_id"] = old_defense_method.defense_method_id
    defense_method["defense_method_name"] = new_defense_method_name
    defense_method["defense_method_prompt"] = new_defense_method_prompt

    db.session.commit()
    db.session.close()

    return defense_method