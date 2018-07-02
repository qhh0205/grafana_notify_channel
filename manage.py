#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/27 下午5:57
# @Author  : haohao.qiang
# @Mail    : haohao.qiang@renren-inc.com
# @File    : manage.py


from flask_script import Manager
from app import create_app

app = create_app()
manager = Manager(app)

if __name__ == '__main__':
    manager.run()
