#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/27 下午5:33
# @Author  : haohao.qiang
# @Mail    : haohao.qiang@renren-inc.com
# @File    : __init__.py.py


import logging
from logging.handlers import TimedRotatingFileHandler
from flask import Flask
from flask_mail import Mail
from config import Config

mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mail.init_app(app)

    register_routes(app)
    register_logger(app)
    return app


def register_routes(app):
    from .handlers import mail, wechat, voice
    app.register_blueprint(mail.bp)
    app.register_blueprint(wechat.bp)
    app.register_blueprint(voice.bp)
    return app


def register_logger(app):
    """日志记录器配置"""
    if app.debug:
        return
    handler = TimedRotatingFileHandler(app.config.get('LOG_PATH', 'app/logs/app.log'),
                                       when=app.config.get('WHEN', 'D'),
                                       backupCount=app.config.get('BACKUP_COUNT', 7))
    fmt = '%(asctime)s|%(levelname)s|%(filename)s:%(lineno)s|%(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(fmt, datefmt=datefmt)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)