# -*— coding:utf-8 -*—
from flask import request, jsonify
from . import model
from .. import db
from ..models import model_info


@model.route('/api/models',methods=['GET'])
def get_models():
    models = list(model_info.query.all())
    model_data = []
    for model in models:
        temp = {
            'model_name': model.model_name,
            'base_url': model.base_url,
            'api_key': model.api_key
        }
        model_data.append(temp)

    return jsonify(model_data)

@model.route('/api/models/info',methods=['GET','POST'])
def get_model_by_model_name():

    data = request.get_json()
    model_name = data["model_name"]

    curr_model = model_info.query.filter_by(model_name=model_name).first()

    # 手动构建字典
    model_data = {
        'base_url': curr_model.base_url,
        'api_key': curr_model.api_key
    }

    return jsonify(model_data)

@model.route('/api/models',methods=['POST'])
def add_model():

    data = request.get_json()
    model_name = data["model_name"]
    base_url = data["base_url"]
    api_key = data["api_key"]

    # 获取攻击方法 id
    model_id = str(len(model_info.query.all()) + 1).zfill(3)

    new_model = model_info(
        model_id = model_id,
        model_name= model_name,
        base_url=base_url,
        api_key=api_key,
    )

    # 返回数据
    new_model_return = {}
    new_model_return["model_id"] = model_id
    new_model_return["model_name"] = model_name
    new_model_return["base_url"] = base_url
    new_model_return["api_key"] = api_key

    # 插入数据库
    db.session.add(new_model)
    db.session.commit()
    db.session.close()

    return new_model_return


@model.route('/api/models',methods=['PUT'])
def modify_model():

    data = request.get_json()
    model_name = data["model_name"]
    new_model_base_url = data["base_url"]
    new_model_api_key = data["api_key"]


    old_model = model_info.query.filter_by(model_name=model_name).first()
    old_model.api_key = new_model_api_key

    # 如果提供了description，则更新
    if new_model_base_url is not None:
        old_model.base_url = new_model_base_url

    # 返回数据
    new_model_return = {}
    new_model_return["model_id"] = old_model.model_id
    new_model_return["model_name"] = model_name
    new_model_return["base_url"] = new_model_base_url
    new_model_return["api_key"] = new_model_api_key

    db.session.commit()
    db.session.close()

    return new_model_return