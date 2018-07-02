#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/27 下午7:08
# @Author  : haohao.qiang
# @Mail    : haohao.qiang@renren-inc.com
# @File    : wechat.py


import sys
import time
import warnings
from datetime import datetime
from flask import abort
from flask import make_response
import json
import requests
from flask import Blueprint, request, current_app, render_template
from ..utils.utils import scheduler, cache

reload(sys)
sys.setdefaultencoding('utf-8')
warnings.filterwarnings("ignore")

__all__ = ['bp']

bp = Blueprint('wechat', __name__)


@bp.route('/wechat', methods=["GET", "POST"])
def wechat_channel():
    req_body     = json.loads(request.data)
    message      = req_body.get('message')
    wechat       = json.loads(message).get('wechat')
    msg          = json.loads(message).get('msg')
    if not wechat or not msg:
        abort(400)
    ts = time.time()
    data = req_body
    data['msg'] = msg
    data['timestamp'] = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
    data['utc_offset'] = int((datetime.fromtimestamp(ts) - datetime.utcfromtimestamp(ts)).total_seconds() / 3600)
    msg = render_template('wechat/wechat.j2', data=data)
    app = current_app._get_current_object()
    scheduler.add_job(wechat_sender, 'date', args=[app, wechat.split(','), '', '', msg])
    return make_response(('OK', 200))


def acquire_token(app, corpid, secret):
    access_token = cache.get('access_token')
    if access_token:
        return access_token
    try:
        token_url = '%s?corpid=%s&corpsecret=%s' % (app.config.get('TOKEN_URL'), corpid, secret)
        response = requests.get(token_url, verify=False)
    except Exception as e:
        app.logger.error(e.message)
        return None

    access_token = response.json().get('access_token')
    if access_token:
        cache['access_token'] = access_token
    return access_token


def wechat_sender(app, touser, toparty, totag, content):
    """
    微信发送接口
    :param touser: 用户微信号
    :param toparty: 部门ID
    :param totag: 标签列表
    :param agentid: 应用ID
    :param content: 消息内容，最长不超过2048个字节
    :return:
    """
    access_token = acquire_token(app, app.config.get('CORPID'), app.config.get('SECRET'))
    if not access_token:
        app.logger.error('Wechat sent to %s failed! Reason: token acquire failed!' % json.dumps(touser))
        return None
    request_url = '%s?access_token=%s' % (app.config.get('REQ_URL'), access_token)
    headers = {'content-type': 'application/json'}
    if len(content) > 2048:
        content = content[:2045] + "..."
    payload = {
        "touser": '|'.join(touser) and '|'.join(touser) or '',
        "toparty": toparty and toparty or '',
        "totag": totag and totag or '',
        "msgtype": "text",
        "agentid": app.config.get('AGENTID'),
        "text": {
            "content": content.encode('UTF-8')
        },
        "safe": "0"
    }

    try:
        response = requests.post(request_url, data=json.dumps(payload, ensure_ascii=False), headers=headers,
                                 verify=False)
        if response.status_code != 200:
            app.logger.error(
                'Wechat sent to %s failed! Reason: %s' % (json.dumps(touser), response.status_code)
            )
        else:
            app.logger.info(
                'Wechat sent to %s successful!' % json.dumps(touser)
            )
    except Exception as e:
        app.logger.error(
            "Wechat sent to %s failed! Reason: %s" % (touser, e.message)
        )
