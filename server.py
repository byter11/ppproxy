import os
from flask import Flask, redirect, jsonify, render_template, request, json, Response
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from _thread import start_new_thread
from cache import Cache, Schedule
from models import db, Filter

app = Flask(__name__)
app.secret_key = "waowaowaowaowaowaowao"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ppproxy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

proxy_cache = Cache(Schedule.LRU)

@app.route('/')
def index():
  return redirect('/admin/filter')

class AdminView(AdminIndexView):
  @expose('/')
  def index(self):
    return self.render('/admin/index.html', schedule=proxy_cache.schedule.value)

@app.route('/log')
def log():
  if os.path.exists('proxy.log'):
    with open('proxy.log') as f:
      return jsonify({"log": f.read()})
  else:
    return jsonify({"log": ""})

@app.route('/schedule', methods=['POST', 'GET'])
def schedule():
  if request.method == 'POST':
    schedule = json.loads(request.data.decode())['schedule']
    print('set', schedule)
    if schedule in [e.value for e in Schedule]:
      proxy_cache.setschedule(Schedule(schedule))
    # return Response('', status=400)
    return {}
  else:
    return proxy_cache.schedule.value


import proxy

admin = Admin(app, index_view=AdminView(), template_mode='bootstrap4')
admin.add_view(ModelView(Filter, db.session))
start_new_thread(proxy.start, (proxy_cache,app))
app.run('0.0.0.0', 8080)