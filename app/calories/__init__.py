from flask import Blueprint

bp = Blueprint('calories', __name__)

from app.calories import routes 