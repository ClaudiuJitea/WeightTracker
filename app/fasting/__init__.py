from flask import Blueprint

bp = Blueprint('fasting', __name__)

from app.fasting import routes 