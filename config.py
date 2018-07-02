#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/27 下午5:15
# @Author  : haohao.qiang
# @Mail    : haohao.qiang@renren-inc.com
# @File    : config.py


class Config(object):
    # 邮件相关配置
    MAIL_SERVER       = ''
    MAIL_PORT         = 587
    MAIL_USE_TLS      = True
    MAIL_USE_SSL      = False
    MAIL_USERNAME     = ''
    MAIL_PASSWORD     = ''
    FLASK_MAIL_SENDER = ''

    # 企业微信相关配置
    AGENTID   = 
    CORPID    = ''
    SECRET    = ''
    TOKEN_URL = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
    REQ_URL   = 'https://qyapi.weixin.qq.com/cgi-bin/message/send'

    # Nexmo 语音电话相关配置
    ANSWER_URL     = ''
    EVENT_URL      = ''
    APPID          = ''
    VIRTUAL_NUMBER = ''
    BASE_URL       = 'https://api.nexmo.com'
    NEXMO_VERSION  = '/v1'
    ACTION         = '/calls'
    KEY_FILE       = ''
    # 打电话失败重试次数
    RETRY_TIMES    = 2

    # Grafana Alert Page
    ALERT_PAGE = ''
