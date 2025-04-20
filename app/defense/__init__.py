# -*— coding:utf-8 -*—
from flask import Blueprint

defense = Blueprint('defense',__name__)

from . import views
