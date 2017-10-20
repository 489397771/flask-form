import os
from PIL import Image
from flask import Flask, render_template
from flask_script import Manager
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from flask_bootstrap import Bootstrap

app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')or'你猜你猜你猜不着'
# 配置上传文件的最大尺寸，默认不限制？？
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 10
# 上传文件保存目录
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(os.getcwd(), 'static\img')
# app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd()
# 文件类型过滤
photos = UploadSet('photos', IMAGES)
# 上传配置
configure_uploads(app, photos)
# 上传文件大小，默认64M，设置为None，会读取配置的MAX_CONTENT_LENGTH的值
patch_request_class(app, size=None)


class UploadForm(FlaskForm):
    photo = FileField(validators=[FileAllowed(photos, '只能上传图片文件'), FileRequired('请选择文件后上传')])
    submit = SubmitField('sub')


@app.route('/', methods=['POST', 'GET'])
def index():
    img_url = None
    form = UploadForm()
    if form.validate_on_submit():
        # 保存文件
        filename = photos.save(form.photo.data)
        # 生成缩略图
        filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
        img = Image.open(filepath)
        img.thumbnail((64, 64))
        img.save(filepath)
        # 获取文件url
        img_url = photos.url(filename)
        print(img_url)
    return render_template('filed.html', form=form, img_url=img_url)


if __name__ == '__main__':
    manager.run()

