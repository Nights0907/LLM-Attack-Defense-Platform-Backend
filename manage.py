# -*— coding:utf-8 -*—
import os
from app import create_app,db
from flask_migrate import Migrate
from flask_script import Manager

# 不同配置选用不同的数据库
app = create_app('development')

migrate = Migrate(app,db)
manager = Manager(app)






