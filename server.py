#!/usr/bin/env python3

from flask import Flask, render_template, url_for, redirect, request, jsonify, send_file, flash, get_flashed_messages, send_from_directory
from flask_login import LoginManager, current_user, user_logged_in
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask_security.signals import password_changed
from flask_security.utils import encrypt_password, verify_password, get_hmac
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email
from datetime import date
import ssl, file_engine, flask_security

app = Flask(__name__)
app.config.from_object('config')

login_manager = LoginManager(app)
db = SQLAlchemy(app)
mail = Mail(app)

roles_users = db.Table('roles_users', db.Column('user_id', db.Integer(), db.ForeignKey('user.id')), db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    def get_name(self):
        return self.name

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(64))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    def is_authenticated(self):
        return True
    def is_active(self):
        return active
    def is_anonymous(self):
        return False
    def get_id(self):
        return self.id
    def get_roles(self):
        return self.roles

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

@security.send_mail_task
def flash_success(msg):
    pass

# @app.before_request
# def sql_update():
#     try:
#         open('/docuserv/data_update', 'r')
#         file_engine.shutil.copyfile('/docuserv/zd.db', '/var/docuserv/zd.db')
#         file_engine.os.remove('/docuserv/data_update')
#     except:
#         pass

def create_user(email, password):
    with app.app_context():
        try:
            newuser = user_datastore.create_user(email=get_hmac(email), password=encrypt_password(password))
            virgin = user_datastore.find_role('Virgin')
            user_datastore.add_role_to_user(newuser, virgin)
            db.session.commit()
        except:
            print('User already exists!')

def change_password(email, password):
    with app.app_context():
        try:
            user = user_datastore.get_user(get_hmac(email))
            user.password = encrypt_password(password)
            virgin = user_datastore.find_role('Virgin')
            user_datastore.add_role_to_user(user, virgin)
            db.session.commit()
        except:
            print('Password change failed!')

def lock_user(email):
    with app.app_context():
        try:
            user = user_datastore.get_user(get_hmac(email))
            locked = user_datastore.find_role('Locked')
            user_datastore.add_role_to_user(user, locked)
            db.session.commit()
        except:
            print('Lock user failed!')

def unlock_user(email):
    with app.app_context():
        try:
            user = user_datastore.get_user(get_hmac(email))
            user_datastore.remove_role_from_user(user, user_datastore.find_role('Locked'))
            db.session.commit()
        except:
            print('Unlock user failed!')

def delete_user(email):
    with app.app_context():
        try:
            user = user_datastore.get_user(get_hmac(email))
            user_datastore.delete_user(user)
            db.session.commit()
        except:
            print('Delete user failed!')

def init_db():
    db.create_all()
    if user_datastore.find_role('Virgin') == None:
        user_datastore.create_role(name='Virgin', description='User to reset password.')
    if user_datastore.find_role('Locked') == None:
        user_datastore.create_role(name='Locked', description='User is locked out.')
    db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@password_changed.connect_via(app)
def pass_changed(sender, user):
    if user.has_role('Virgin'):
        user_datastore.remove_role_from_user(user, user_datastore.find_role('Virgin'))

@app.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    pass

@app.route('/reset')
def reset():
    pass

@app.route('/change')
def change():
    pass

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.has_role('Virgin'):
        return redirect(url_for('change', virgin=True))
    if current_user.has_role('Locked'):
        return redirect(url_for('logout'))
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

    teacher = args.get('teacher')
    if teacher == '':
        teacher = 'All'

    if args.get('mf') == 'false':
        upfile = request.files['file']
        # file_engine.add_file(args.get('class'), upfile, upfile.filename, args.get('type').capitalize(), downloadable, quarter, args.get('year'), current_user.email.decode())
        file_engine.add_file(args.get('class'), upfile, upfile.filename, args.get('type').capitalize(), downloadable, quarter, args.get('year'), current_user.email.decode(), teacher)
    else:
        for i in range(len(request.files)):
            upfile = request.files['file'+'[' + str(i) + ']']
            # file_engine.add_file(args.get('class'), upfile, upfile.filename, args.get('type').capitalize(), downloadable, quarter, args.get('year'), current_user.email.decode())
            file_engine.add_file(args.get('class'), upfile, upfile.filename, args.get('type').capitalize(), downloadable, quarter, args.get('year'), current_user.email.decode(), teacher)
    file_engine.update_active()
    return 'OK', 200

@app.route('/_validate')
@login_required
def validate():
    error_list = list()
    upload_type = request.args.get('upload', type=str)
    quarter = request.args.get('quarter', type=str)
    year = request.args.get('year', type=str)
    downloadable = request.args.get('downloadable', type=str)
    classcode = request.args.get('class', type=str)

    if upload_type.lower() not in ['lab', 'quiz', 'test', 'homework', 'paper', 'project', 'textbook', 'syllabus']:
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
    if len(error_list) > 0:
        error_list.append('See Help for more information.')
    return jsonify(error=error_list)

@app.route('/_get_class')
@login_required
def get_class():
    code = request.args.get('code', type=str)
    num = request.args.get('num', type=str)
    return jsonify(info=file_engine.file_list(code, num, current_user.email.decode()))

@app.route('/_search_all')
@login_required
def search_all():
    term = request.args.get('term', type=str)
    return jsonify(info=file_engine.search_all(term, current_user.email.decode()))

@app.route('/_class_container_update')
@login_required
def class_container_update():
    return jsonify(class_container=file_engine.active)

@app.route('/_file_view')
@login_required
def file_view():
    image_list = file_engine.get_images(request.args.get('path') + '-images', request.args.get('page', type=int))
    return jsonify(image_list)

@app.route('/_file_view_pdf')
@login_required
def file_view_pdf():
    path = request.args.get('path')
    pdf = file_engine.get_pdf(path)
    if pdf == False:
        return 'Nothing to show'
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        'inline; filename=%s.pdf' % 'yourfilename'
    # return response
    # f = open('/docuserv/test', 'w')
    # f.write(pdf)
    # f.flush()
    # f.close()
    return jsonify(response)

@app.route('/_file_view_previous')
@login_required
def file_view_p():
    image_list = file_engine.get_previous_images(request.args.get('path') + '-images', request.args.get('page', type=int))
    return jsonify(image_list)

@app.route('/_file_view_next')
@login_required
def file_view_n():
    image_list = file_engine.get_next_images(request.args.get('path') + '-images', request.args.get('page', type=int))
    return jsonify(image_list)

@app.route('/_file_serve')
@login_required
def file_serve():
    return send_file(request.args.get('file'), as_attachment=True, attachment_filename=request.args.get('name') + '.' + request.args.get('extension'))

@app.route('/_del_file')
@login_required
def delete_file():
    code = request.args.get('code', type=str)
    num = request.args.get('num', type=str)
    file_engine.delete_file(' '.join([code, num]), request.args.get('hashpath', type=str), current_user.email.decode())
    file_engine.update_active()
    return 'DELETED'

@app.route('/.well-known/acme-challenge/<token_value>')
def letsencrpyt(token_value):
    with open('.well-known/acme-challenge/{}'.format(token_value)) as f:
        answer = f.readline().strip()
    return answer

init_db()
file_engine.update_active()
# app.run(debug=True, ssl_context=context, host='0.0.0.0')
if __name__ == '__main__':
    file_engine.update_active()
    init_db()
    app.run(debug=True, host='0.0.0.0', port=7000, threaded=True)
