from flask import Flask, render_template, request
from flask_script import Manager
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class
import os

app = Flask(__name__)
manager = Manager(app)

# 配置上传文件的最大尺寸，默认不限制？？
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 10
# 上传文件保存目录
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd()
# 文件类型过滤
photos = UploadSet('photos', IMAGES)
# 上传配置
configure_uploads(app, photos)
# 上传文件大小，默认64M，设置为None，会读取配置的MAX_CONTENT_LENGTH的值
patch_request_class(app, size=None)


@app.route('/', methods=['POST', 'GET'])
def index():
    img_url = None
    if request.method == 'POST' and 'photo' in request.files:
        # 保存文件
        filename = photos.save(request.files['photo'])
        # 获取文件url
        img_url = photos.url(filename)
    return render_template('filed.html', img_url=img_url)


if __name__ == '__main__':
    manager.run()

