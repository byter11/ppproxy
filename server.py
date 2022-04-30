import os
from flask import Flask, redirect, jsonify
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from _thread import start_new_thread
import proxy
from models import db, Filter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ppproxy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

admin = Admin(app, name="Admin", template_mode='bootstrap3')

admin.add_view(ModelView(Filter, db.session))

@app.route('/')
def index():
	return redirect('/admin/filter')

@app.route('/log')
def log():
	if os.path.exists('proxy.log'):
		with open('proxy.log') as f:
			return jsonify({"log": f.read()})
	else:
		return jsonify({"log": ""})

start_new_thread(proxy.start, ())
app.run('0.0.0.0', 8080)