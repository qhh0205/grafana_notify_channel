#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/27 下午7:08
# @Author  : haohao.qiang
# @Mail    : haohao.qiang@renren-inc.com
# @File    : mail.py


import time
import json
from datetime import datetime
from flask import abort
from flask_mail import Message
from flask import make_response
from flask import Blueprint, request, current_app, render_template
from .. import mail
from ..utils.utils import scheduler


__all__ = ['bp']

bp = Blueprint('mail', __name__)


@bp.route('/mail', methods=["GET", "POST"])
def mail_channel():
    req_body = json.loads(request.data)
    message = req_body.get('message')
    mails = [m.strip() for m in json.loads(message).get('mail').split(',')]
    content = json.loads(message).get('content')
    if not mails or not content:
        abort(400)
    ts = time.time()
    data = req_body
    data['content'] = content
    data['timestamp'] = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
    data['utc_offset'] = int((datetime.fromtimestamp(ts) - datetime.utcfromtimestamp(ts)).total_seconds() / 3600)
    data['alertPage'] = current_app.config.get('ALERT_PAGE')
    app = current_app._get_current_object()
    scheduler.add_job(send_mail,
                      'date',
                      args=[app, mails, data.get('title'), render_template('mail/mail.j2', data=data)]
                 )
    return make_response(('OK', 200))


def send_mail(app, to, subject, content):
    msg = Message(subject,
                  sender=app.config.get('FLASK_MAIL_SENDER'),
                  recipients=to)
    msg.html = content
    with app.app_context():
        mail.send(msg)
        app.logger.info('Mail sent to %s successful!' % json.dumps(to))
