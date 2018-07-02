#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/27 下午7:08
# @Author  : haohao.qiang
# @Mail    : haohao.qiang@renren-inc.com
# @File    : voice.py


import datetime
from flask import jsonify
from flask import abort
from flask import make_response
import json
import uuid
import requests
from flask import Blueprint, request, current_app, render_template
from ..utils.utils import scheduler, cache
from ..utils.jwt import generate_jwt

__all__ = ['bp']

bp = Blueprint('voice', __name__)


@bp.route('/voice', methods=["POST"])
def voice_channel():
    req_body = json.loads(request.data)
    message = req_body.get('message')
    phone_list = json.loads(message).get('phone').split(',')
    text_to_speech = json.loads(message).get('text_to_speech')
    if not phone_list or not text_to_speech:
        abort(400)

    data = req_body
    data['text_to_speech'] = text_to_speech
    text_to_speech = render_template('voice/voice.j2', data=data)
    # Nexmo 限制语音信息字符数最多为 1500, 在此做截断处理, 避免超出限制
    if len(text_to_speech) > 1500:
        text_to_speech = text_to_speech[:1450] + "..."
    app = current_app._get_current_object()
    for number in phone_list:
        cache_key = str(uuid.uuid1())
        cache[cache_key] = {'phone': number, 'msg': text_to_speech, 'retry_times': app.config.get('RETRY_TIMES', 2)}
        scheduler.add_job(make_call, 'date',
                          run_date=(datetime.datetime.now() + datetime.timedelta(seconds=len(scheduler.get_jobs()) + 1)),
                          args=[app, number, cache_key]
                          )

    return make_response(('OK', 200))


@bp.route('/nexmo/answer/<uuid>', methods=["GET", "POST"])
def nexmo_answer(uuid):
    item = cache.get(str(uuid))
    if item:
        ncco = [
            {
                "action": "talk",
                "text": item.get('msg'),
                "loop": 5
            }
        ]
        return jsonify(ncco)
    current_app.logger.error('Cached %s expired!' % item)
    abort(500)


@bp.route('/nexmo/event/<uuid>', methods=["GET", "POST"])
def nexmo_event(uuid):
    item = cache.get(str(uuid))
    if not item:
        abort(500)
    rest_retry_times = item.get('retry_times')
    number = item.get('phone')
    req_body = json.loads(request.data)
    call_status = req_body.get('status')

    if call_status not in ["timeout", "failed", "rejected", "cancelled", "busy", "unanswered"]:
        current_app.logger.info(str(req_body))
        if call_status in ["completed"]:
            cache.pop(uuid)
    elif rest_retry_times > 0:
        cache[uuid]['retry_times'] = (rest_retry_times - 1)
        app = current_app._get_current_object()
        scheduler.add_job(make_call, 'date',
                          run_date=(datetime.datetime.now() + datetime.timedelta(seconds=len(scheduler.get_jobs())+1)),
                          args=[app, str(number), uuid])
        current_app.logger.error(str(req_body))
    else:
        cache.pop(uuid)
    return make_response(('OK', 200))


def make_call(app, number, cache_key):
    jwt = generate_jwt(app.config.get('APPID'),
                       app.config.get('KEY_FILE', 'app/handlers/secret/application_secret_key.txt'))
    # Create the headers using the jwt
    headers = {
        "Content-type": "application/json",
        "Authorization": "Bearer {0}".format(jwt)
    }

    payload = {
        "to": [{
            "type": "phone",
            "number": number
        }],
        "from": {
            "type": "phone",
            "number": app.config.get('VIRTUAL_NUMBER')
        },
        "answer_url": [app.config.get('ANSWER_URL') + cache_key],
        "event_url": [app.config.get('EVENT_URL') + cache_key]
    }
    response = requests.post(app.config.get('BASE_URL', 'https://api.nexmo.com')
                             + app.config.get('NEXMO_VERSION', '/v1')
                             + app.config.get('ACTION', '/calls'),
                             data=json.dumps(payload, ensure_ascii=False),
                             headers=headers,
                             verify=False)
    app.logger.info(response.text)
    return response.status_code
