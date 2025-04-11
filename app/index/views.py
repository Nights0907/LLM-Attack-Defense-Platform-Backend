# -*— coding:utf-8 -*—
from flask import render_template, Response, request, jsonify
from . import index, logs
from ..utils.renellm.log_utils import generate_logs


@index.route('/index',methods=['GET','POST'])
def _index():
    return render_template('index.html')

@logs.route('/logs')
def stream_logs():
    response = Response(generate_logs(), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response
