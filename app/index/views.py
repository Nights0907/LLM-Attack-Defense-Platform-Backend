# -*— coding:utf-8 -*—
import csv

import requests
from flask import render_template, Response, request
from . import index, logs
from .. import db
from ..models import malicious_questions_model
from app.utils.log_utils import generate_logs
from ..utils.llm_completion_utils import get_llm_responses, get_llm_responses_stream


@index.route('/index',methods=['GET','POST'])
def _index():
    return render_template('index.html')

@logs.route('/api/logs',methods=['GET','POST'])
def stream_logs():

    response = Response(generate_logs(), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"

    return response


@logs.route('/data')
# 将问题集存入数据库
def data_save():
    # 添加到数据库
    data_path = "E:\\BMIS-main\\app\\data\\codechameleon\\all_problem.csv"
    with open(data_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        id = 0
        for row in reader:
            goal = row[1]
            set = row[0]
            question = malicious_questions_model(question_id=id, question_goal=goal, question_target="", question_set=set)
            db.session.add(question)
            id += 1
        db.session.commit()
    return "success"


@logs.route('/test')
# 将问题集存入数据库
def get_llm_res():
    data = request.get_json()
    content = data["content"]
    model = data["model"]
    messages = [{"role":"user","content":content}]
    attack_output = get_llm_responses_stream(model,messages,0,1,True)
    return attack_output