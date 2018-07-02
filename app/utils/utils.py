#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/27 下午7:14
# @Author  : haohao.qiang
# @Mail    : haohao.qiang@renren-inc.com
# @File    : utils.py


import logging
from expiringdict import ExpiringDict

#  Python 任务调度框架: APScheduler https://apscheduler.readthedocs.io/en/latest/index.html
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

logging.basicConfig(filename='app/logs/app.log', level=logging.INFO,
                    format='%(asctime)s|%(levelname)s|%(filename)s:%(lineno)s|%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
       )

executors = {
    'threadpool': ThreadPoolExecutor(50)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 50
}

scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)
scheduler.start()

cache = ExpiringDict(max_len=1024, max_age_seconds=1800)