import os
import uuid
from threading import Thread
from PIL import Image

from flask import Flask, session, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_script import Manager
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, PasswordField, DateTimeField, ValidationError
from wtforms.validators import DataRequired, Length, Email
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class
from flask_mail import Mail, Message


app = Flask(__name__)
# 密钥配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')or'你猜你猜你猜不着'
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
# 配置上传文件的最大尺寸，默认不限制
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 10
# 上传文件保存目录
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(os.getcwd(), 'static\img')
# 文件类型过滤
photos = UploadSet('photos', IMAGES)
# 上传配置
configure_uploads(app, photos)
# 上传文件大小，默认64M，设置为None，会读取配置的MAX_CONTENT_LENGTH的值
patch_request_class(app, size=None)

# 邮箱配置
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER') or 'smtp.163.com'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') or 'zhentaoyangs7@163.com'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') or '6188690iswO'
bootstrap = Bootstrap(app)
manager = Manager(app)
mail = Mail(app)


class NameForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(1, 12)])
    # length(6, 12, message='6~12字符')message 是指定输入格式错误提示
    password = PasswordField('password', validators=[DataRequired(), Length(6, 12)])
    mail = StringField('user email', validators=[DataRequired(), Email()])
    time = DateTimeField('create time')
    photo = FileField('user picture', validators=[FileRequired(), FileAllowed(photos)])
    submit = SubmitField('submit')

    # 自定义验证器，格式：‘validate_字段’。仅限于验证信息后提示错误信息用
    # 以validate_开头的函数会自动校验'_'后面的对应名字的字段
    # 此函数功能和length()功能差不多，只是作为演示例子用
    # def validate_username(self, field):
    #     if len(field.data) < 6:
    #         raise ValidationError('不能少于6个字符')


# 随机生成的字符串
def rand_str(length=32):
    return str(uuid.uuid4())[0:length]


# 异步发送邮箱任务
def async_send_mail(app, msg):
    # 发送邮箱需要程序的上下文，否则无法发送
    # 在新的线程中没有上下文，需要手动创建
    with app.app_context():
        mail.send(msg)


# 发送邮件函数
def send_mail(to, subject, template, **kwargs):
    msg = Message(subject=subject, sender=app.config['MAIL_USERNAME'],recipients=[to])
    msg.body = render_template(template + '.txt')
    msg.html = render_template(template + '.html')
    # 创建线程
    thr = Thread(target=async_send_mail, args=[app, msg])
    thr.start()
    return thr


@app.route('/')
def index():
    return 'success'


@app.route('/form/', methods=['POST', 'GET'])
def show():
    form = NameForm()
    if form.validate_on_submit():
        flash('欢迎' + form.username.data + '光临')
        session['username'] = form.username.data
        session['email'] = form.mail.data
        suffix = os.path.splitext(request.files['photo'].filename)[1]
        name = rand_str() + suffix

        # 保存文件
        filename = photos.save(form.photo.data, name=name)
        # 生成缩略图
        filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
        img = Image.open(filepath)
        img.thumbnail((64, 64))
        img.save(filepath)
        # 获取文件url
        img_url = photos.url(filename)
        session['img_url'] = img_url
        return redirect(url_for('show'))
    name = session.get('username')
    img_url = session.get('img_url')
    email = session.get('email')
    try:
        send_mail(email, '激活验证信息', 'account', name=name)
        if email is not None:
            flash('激活信息已发送，请到注册邮箱中查收')
    except TypeError as e:
        pass
    return render_template('index.html', form=form, name=name, img_url=img_url)


@app.route('/session_clc/')
def session_clc():
    if session.get('username') is not None:
        name = session['username']
        session.clear()
        flash('已清除' + name + '的所有信息')
    else:
        flash('无用户信息,无需注销')
    return redirect(url_for('show'))


if __name__ == '__main__':
    manager.run()

