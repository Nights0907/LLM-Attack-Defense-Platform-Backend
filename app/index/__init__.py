# -*— coding:utf-8 -*—
from flask import Blueprint

index = Blueprint('index',__name__)
logs = Blueprint('logs',__name__)
logging = Blueprint('logging',__name__)

from . import views
