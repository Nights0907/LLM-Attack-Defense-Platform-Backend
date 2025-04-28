from flask import request, jsonify

from . import defense
from .. import db
from ..models import defense_method_info


@defense.route('/api/defense', methods=['POST'])
# @login_required 暂时不需要用户登录
def add_attack_method():
    data = request.get_json()
    defense_method_name = data["defense_method_name"]
    defense_method_prompt = data["defense_method_prompt"]
    # 获取description字段，如果不存在则设为空字符串
    defense_method_description = data.get("defense_method_description", "")

    # 获取攻击方法 id
    defense_method_id = str(len(defense_method_info.query.all()) + 1).zfill(3)

    new_method = defense_method_info(
        defense_method_id=defense_method_id,
        defense_method_name=defense_method_name,
        defense_method_prompt=defense_method_prompt,
        defense_method_description=defense_method_description
    )

    # 返回数据
    defense_method = {}
    defense_method["defense_method_id"] = defense_method_id
    defense_method["defense_method_name"] = defense_method_name
    defense_method["defense_method_prompt"] = defense_method_prompt
    defense_method["defense_method_description"] = defense_method_description

    # 插入数据库
    db.session.add(new_method)
    db.session.commit()
    db.session.close()

    return defense_method


@defense.route('/api/defense', methods=['PUT'])
# @login_required 暂时不需要用户登录
def modify_defense_method():
    data = request.get_json()
    old_defense_method_name = data["old_defense_method_name"]
    new_defense_method_name = data["new_defense_method_name"]
    new_defense_method_prompt = data["new_defense_method_prompt"]
    # 获取description字段，如果不存在则保持原值
    new_defense_method_description = data.get("new_defense_method_description", None)

    old_defense_method = defense_method_info.query.filter_by(defense_method_name=old_defense_method_name).first()
    old_defense_method.defense_method_name = new_defense_method_name
    old_defense_method.defense_method_prompt = new_defense_method_prompt

    # 如果提供了description，则更新
    if new_defense_method_description is not None:
        old_defense_method.defense_method_description = new_defense_method_description

    # 返回数据
    defense_method = {}
    defense_method["defense_method_id"] = old_defense_method.defense_method_id
    defense_method["defense_method_name"] = new_defense_method_name
    defense_method["defense_method_prompt"] = new_defense_method_prompt
    defense_method["defense_method_description"] = old_defense_method.defense_method_description

    db.session.commit()
    db.session.close()

    return defense_method


@defense.route('/api/defense', methods=['DELETE'])
# @login_required 暂时不需要用户登录
def delete_defense_method():
    """
    删除指定的防御方法

    接收URL参数中的defense_method_name，删除对应的防御方法
    """
    # 获取URL参数中的防御方法名称
    defense_method_name = request.args.get('defense_method_name')

    if not defense_method_name:
        return jsonify({'error': 'Missing defense_method_name parameter'}), 400

    # 查找要删除的防御方法
    method_to_delete = defense_method_info.query.filter_by(defense_method_name=defense_method_name).first()

    if not method_to_delete:
        return jsonify({'error': f'Defense method {defense_method_name} not found'}), 404

    try:
        # 从数据库中删除
        db.session.delete(method_to_delete)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Defense method {defense_method_name} deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete defense method: {str(e)}'}), 500
    finally:
        db.session.close()


@defense.route('/api/defense/methods', methods=['GET'])
# @login_required 暂时不需要用户登录
def get_all_defense_methods():
    """
    获取所有防御方法列表

    返回所有防御方法的列表，包含id、名称和提示词
    """
    try:
        methods = defense_method_info.query.all()
        result = []

        for method in methods:
            result.append({
                "id": method.defense_method_id,
                "name": method.defense_method_name,
                "prompt": method.defense_method_prompt,
                "description": method.defense_method_description
            })

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to get defense methods: {str(e)}'}), 500