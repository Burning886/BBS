# @Author:WY
# @Time:2020/2/1016:39

# 前台 后台 公共的

from flask import Flask
from apps.cms import cms
from apps.common import common
from apps.front import front
import config
from exts import db, mail
from flask_wtf import CSRFProtect
from uEditor import ueditor


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    app.register_blueprint(cms)
    app.register_blueprint(common)
    app.register_blueprint(front)
    app.register_blueprint(ueditor)
    db.init_app(app)
    mail.init_app(app)
    CSRFProtect(app)
    return app



if __name__ == '__main__':
    app = create_app()
    app.run()
