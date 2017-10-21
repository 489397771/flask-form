from flask import Blueprint
import os
import uuid
import datetime
from PIL import Image

from flask import session, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email
from flask_uploads import UploadSet, IMAGES
import sqlalchemy
# 要在蓝本引入app必须在user下面引入才可以！！！！

user = Blueprint('user', __name__)
from manage import send_mail, photos, app, db

# 文件类型过滤
photos = UploadSet('photos', IMAGES)


# 随机生成的字符串
def rand_str(length=32):
    return str(uuid.uuid4())[0:length]


# 定义模型
class User(db.Model):
    #  可指定表名，若不指定表名，会默认将模型类名的‘小写+下划线’
    # 如：模型名为UserModel，则默认表名为user_model
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(32))
    email = db.Column(db.String(64), unique=True)
    imgpath = db.Column(db.String(128), unique=True)
    time = db.Column(db.DateTime(), unique=True)
    delete = db.Column(db.Boolean(), default=1)


# 表单类
class NameForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(1, 12)])
    # length(6, 12, message='6~12字符')message 是指定输入格式错误提示
    password = PasswordField('password', validators=[DataRequired(), Length(6, 12)])
    mail = StringField('user email', validators=[DataRequired(), Email()])
    photo = FileField('user picture', validators=[FileRequired(), FileAllowed(photos)])
    submit = SubmitField('submit')


# 存入数据库
def save_sql(name, pawd, mail, photo, time):
    db.create_all()
    per = User(username=name, password=pawd, email=mail, imgpath=photo, time=time)
    db.session.add(per)
    db.session.commit()


@user.route('/login/', methods=['POST', 'GET'])
def show():
    img_url = None
    form = NameForm()
    if form.validate_on_submit():
        flash('欢迎' + form.username.data + '光临')
        session['username'] = form.username.data
        username = form.username.data
        email = form.mail.data
        password = form.password.data
        time = datetime.datetime.now()
        # session['email'] = form.mail.data
        suffix = os.path.splitext(request.files['photo'].filename)[1]
        name = rand_str() + suffix
        # 保存文件 name指定文件名字
        filename = photos.save(form.photo.data, name=name)
        # 生成缩略图
        filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
        img = Image.open(filepath)
        img.thumbnail((64, 64))
        img.save(filepath)
        # 获取文件url
        imgpath = photos.url(filename)
        save_sql(username, password, email, imgpath, time)
        return redirect(url_for('user.show'))
    name = session.get('username')
    try:
        user = User.query.filter_by(username=name).first()
        email = user.email
        img_url = user.imgpath
        send_mail(email, '激活验证信息', 'account', name=name)
        if email is not None:
            flash('激活信息已发送，请到注册邮箱中查收')
    except sqlalchemy.exc.ProgrammingError:
        db.create_all()
    except AttributeError:
        pass
    return render_template('index.html', form=form, name=name, img_url=img_url)


@user.route('/session_clc/')
def session_clc():
    if session.get('username') is not None:
        name = session['username']
        session.clear()
        flash('已清除' + name + '的所有信息')
    else:
        flash('无用户信息,无需注销')
    return redirect(url_for('user.show'))



