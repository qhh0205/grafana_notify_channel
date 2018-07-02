#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# @Time    : 2018/6/19 上午10:43
# @Author  : qianghaohao
# @Mail    : haohao.qiang@renren-inc.com
# @File    : setup_venv.sh


set -e
cd `dirname $0`
if ! command -v virtualenv >/dev/null 2>&1; then
    pip install --user virtualenv
fi
if [ ! -d 'venv' ]; then
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi
source venv/bin/activate
exit 0
