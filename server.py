#!/usr/bin/env python3

from flask import Flask, render_template, url_for, redirect, request, jsonify
from flask_login import LoginManager, current_user
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email
from datetime import date
import ssl, file_engine

# context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
# context.load_cert_chain('localhost.crt', 'localhost.key')

app = Flask(__name__)
app.config.from_object('config')

login_manager = LoginManager(app)
db = SQLAlchemy(app)

roles_users = db.Table('roles_users', db.Column('user_id', db.Integer(), db.ForeignKey('user.id')), db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))
file_engine.update_active()

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(64))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    # Flask-Login integration
    def is_authenticated(self):
        return True
    def is_active(self): # line 37
        return active
    def is_anonymous(self):
        return False
    def get_id(self):
        return self.id

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create a user to test with
@app.before_first_request
def create_user():
    db.create_all()
    user_datastore.create_user(email='rohin@uchicago.edu', password='HelloWorld!')
    db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    pass

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', collap=file_engine.active)

@app.route('/logout')
@login_required
def logout():
    pass

@app.route('/_file_upload', methods=['POST'])
@login_required
def upload():
    args = request.args

    downloadable = args.get('downloadable').lower()
    if downloadable == 'y':
        downloadable = 'yes'
    if downloadable == 'n':
        downloadable = 'no'
    downloadable = downloadable.capitalize()

    quarter = args.get('quarter').lower()
    if quarter == 'f':
        quarter = 'fall'
    if quarter == 'w':
        quarter = 'winter'
    if quarter == 's':
        quarter = 'spring'
    if quarter == 'su':
        quarter = 'summer'
    quarter = quarter.capitalize()

    if args.get('mf') == 'false':
        upfile = request.files['file']
        file_engine.add_file(args.get('class'), upfile, upfile.filename, args.get('type').capitalize(), downloadable, quarter, args.get('year'))
    else:
        for i in range(len(request.files)):
            upfile = request.files['file'+'[' + str(i) + ']']
            file_engine.add_file(args.get('class'), upfile, upfile.filename, args.get('type').capitalize(), downloadable, quarter, args.get('year'))
    file_engine.update_active()
    return 'OK', 200

@app.route('/_validate')
@login_required
def validate():
    error_list = list()
    uplodad_type = request.args.get('upload', type=str)
    quarter = request.args.get('quarter', type=str)
    year = request.args.get('year', type=str)
    downloadable = request.args.get('downloadable', type=str)
    classcode = request.args.get('class', type=str)

    if uplodad_type.lower() not in ['lab', 'test', 'homework', 'paper', 'project', 'textbook', 'syllabus']:
        error_list.append('Upload type is not supported.')
    if  quarter.lower() not in ['f', 'w', 's', 'su', 'fall', 'winter', 'summer', 'spring']:
        error_list.append('Quarter not valid.')
    if not year.isdigit() or len(year) != 4 or int(year) < 1996 or int(year) > date.today().year:
        error_list.append('Year not valid.')
    if downloadable.lower() not in ['y', 'n', 'yes', 'no']:
        error_list.append('Downloadable must be either Y/N.')
    try:
        code, num = classcode.split()
        if not file_engine.check_whitelist(code, num):
            error_list.append('Class not valid.')
    except:
        error_list.append('Class format not correct.')
    return jsonify(error=error_list)

@app.route('/_get_class')
@login_required
def add_numbers():
    code = request.args.get('code', type=str)
    num = request.args.get('num', type=str)
    return jsonify(info=file_engine.file_list(code, num))

@app.route('/_class_container_update')
@login_required
def class_container_update():
    return jsonify(class_container=file_engine.active)

@app.route('/file_view_test')
def tester():
    return '<p>poop</p><object width="400" height="400" data="/server.py"></object>'

# app.run(debug=True, ssl_context=context, host='0.0.0.0')
app.run(debug=True, host='0.0.0.0', threaded=True)
