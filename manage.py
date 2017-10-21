import os
from threading import Thread
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_script import Manager, Shell
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class
from flask_mail import Mail, Message
from flask_migrate import MigrateCommand, Migrate
from user import user

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
mail = Mail(app)
bootstrap = Bootstrap(app)
manager = Manager(app)


# 数据库配置
Database_uri = 'mysql://root:122121@127.0.0.1:3306/flask_test1'
app.config['SQLALCHEMY_DATABASE_URI'] = Database_uri
# 禁止对象更改追踪
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 配置自动提交(在请求结束时自动执行提交操作)
# 否则每次数据提
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# 引入蓝本
app.register_blueprint(user, url_prefix='/user')
# 创建对象
db = SQLAlchemy(app)
# 创建迁移对象
migrate = Migrate(app, db)
# 添加终端生成命令
manager.add_command('db', MigrateCommand)


# 异步发送邮箱任务
def async_send_mail(app, msg):
    # 发送邮箱需要程序的上下文，否则无法发送
    # 在新的线程中没有上下文，需要手动创建
    with app.app_context():
        mail.send(msg)


# 发送邮件函数
def send_mail(to, subject, template, **kwargs):
    msg = Message(subject=subject, sender=app.config['MAIL_USERNAME'], recipients=[to])
    msg.body = render_template(template + '.txt', name=kwargs.get('name'))
    msg.html = render_template(template + '.html', name=kwargs.get('name'))
    # 创建线程
    thr = Thread(target=async_send_mail, args=[app, msg])
    thr.start()
    return thr


def shell_maka_context():
    # 返回的数据作为shell启动时的上下文
    return dict(db=db, user=user, app=app)


manager.add_command('shell', Shell(make_context=shell_maka_context()))


@app.route('/')
def index():
    return render_template('base.html')


if __name__ == '__main__':
    manager.run()

