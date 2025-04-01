# -*— coding:utf-8 -*—
from flask import Blueprint

attack = Blueprint('attack',__name__)

from . import views
