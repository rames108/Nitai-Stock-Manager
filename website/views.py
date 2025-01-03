from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Item
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    low_stock = Item.query.filter(Item.intItemStock < Item.intItemMin).all()
    return render_template("home.html", low_stock=low_stock, user=current_user)
