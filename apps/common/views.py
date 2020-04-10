# @Author:WY
# @Time:2020/2/1016:45
from flask import Blueprint, jsonify
import qiniu

common = Blueprint("common", __name__, url_prefix="/common")


@common.route("/")
def index():
    return "common index"


@common.route('/uptoken/')
def uptoken():
    access_key = '0JtkthKCUECaoNtU0nWqvC36Td2A-Mc0VmlU2ZFt'
    secret_key = 'BBoYjVPMXeOGPz3D2oAB4M_CUM33iVEcnaYj4kaq'
    q = qiniu.Auth(access_key, secret_key)

    bucket = 'wyvideo8'
    token = q.upload_token(bucket)
    return jsonify({'uptoken': token})
