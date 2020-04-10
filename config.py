# @Author:WY
# @Time:2020/2/1016:41

import os

DEBUG = True
SQLALCHEMY_DATABASE_URI = 'mysql+cymysql://root:123456@localhost:3306/bbs'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.urandom(24)

CMS_USER_ID = "abcdefg"
FRONT_USER_ID = 'sjaojai23jkojaodn'
# 发送者邮箱的服务地址
MAIL_SERVER = "smtp.qq.com"
MAIL_PORT = "587"
MAIL_USE_TLS = True
# MAIL_USE_SSL : default False
MAIL_USERNAME = "1306219607@qq.com"
MAIL_PASSWORD = "bqjrbhbupucogdcd"
MAIL_DEFAULT_SENDER = "1306219607@qq.com"

# uEditor配置
UEDITOR_UPLOAD_TO_QINIU = True
UEDITOR_QINIU_ACCESS_KEY = "0JtkthKCUECaoNtU0nWqvC36Td2A-Mc0VmlU2ZFt"
UEDITOR_QINIU_SECRET_KEY = "BBoYjVPMXeOGPz3D2oAB4M_CUM33iVEcnaYj4kaq"
UEDITOR_QINIU_BUCKET_NAME = "wyvideo8"
UEDITOR_QINIU_DOMAIN = "http://q717fy1qt.bkt.clouddn.com/"

# flask_paginate的相关配置
PER_PAGE = 10
