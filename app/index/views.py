# -*— coding:utf-8 -*—
import csv

from flask import render_template, Response
from . import index, logs
from .. import db
from ..models import malicious_questions_model
from app.utils.log_utils import generate_logs


@index.route('/index',methods=['GET','POST'])
def _index():
    return render_template('index.html')

@logs.route('/logs')
def stream_logs():

    response = Response(generate_logs(), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    response.headers["charset"] = "utf-8"

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
