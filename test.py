from flask import Flask, render_template, request, send_from_directory, url_for
from flask_script import Manager
import os
app = Flask(__name__)
manager = Manager(app)
# 判断是否允许是允许上传的文件后缀
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png', 'gif'])
# 配置上传文件的最大尺寸，默认不限制？？
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 10
# 上传文件保存目录
app.config['UPLOAD_FOLDER'] = os.getcwd()


# 判断是否允许是允许的文件后缀
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# 生成随机的字符串
def rand_str(length=32):
    import random
    base_str = 'qwertyuioplkjhgfdsazxcvbnm1234567890'
    return ''.join(random.choice(base_str) for i in range(length))


@app.route('ow/<imagename>/')
def show(imagename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],imagename)


@app.route('/', methods=['POST', 'GET'])
def index():
    img_url = None
    if request.method == 'POST':
        file = request.files.get('photo')
        if file and allowed_file(file.filename):
            # 生成随机文件名
            suffix = os.path.splitext(file.filename)[1]
            filename = rand_str() + suffix
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img_url = url_for('show', imagename=filename)
    return render_template('index.html', img_url=img_url)


if __name__ == '__main__':
    manager.run()
