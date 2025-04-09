# -*— coding:utf-8 -*—

# flask框架 所需包
from flask import render_template,Response

# LLM attack 所需包
from . import index, logs ,logging
from ..utils.renellm.log_utils import generate_logs


@index.route('/index',methods=['GET','POST'])
def _index():
    return render_template('index.html')

@logs.route('/logs',methods=['GET','POST'])
def _logs():
    return Response(generate_logs(), content_type='text/event-stream')

@logging.route('/start-logging', methods=['GET'])
def start_logging():
    # 返回日志流
    return Response(generate_logs(), content_type='text/event-stream')


