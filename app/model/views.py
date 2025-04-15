# -*— coding:utf-8 -*—
from flask import render_template, Response, request, jsonify
from . import model
from ..models import model_info


@model.route('/api/models',methods=['GET','POST'])
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

