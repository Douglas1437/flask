from flask import Flask
from views_admin import admin_blueprint
from views_news import news_blueprint
from views_user import user_blueprint
import os


def create_app(config):
    app = Flask(__name__)
    # 从配置对象中加载配置
    app.config.from_object(config)

    # 注册蓝图
    app.register_blueprint(news_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(admin_blueprint)

    import logging
    from logging.handlers import RotatingFileHandler
    # 设置⽇志的记录等级
    logging.basicConfig(level=logging.DEBUG)  # 调试debug级

    # 创建⽇志记录器，指明⽇志保存的路径、每个⽇志⽂件的最⼤⼤⼩、保存的⽇志⽂件个数上限
    file_log_handler = RotatingFileHandler(config.BASE_DIR + '/logs/xjzx.log', maxBytes=1024 * 1024 * 100, backupCount
    =10)
    # 创建⽇志记录的格式：⽇志等级、输⼊⽇志信息的⽂件名、⾏数、⽇志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的⽇志记录器设置⽇志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的⽇志⼯具对象添加⽇记录器
    logging.getLogger().addHandler(file_log_handler)
    app.logger_xjzx = logging

    return app
