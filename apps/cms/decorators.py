# @Author:WY
# @Time:2020/2/1020:32
from flask import session, redirect, url_for, g
from functools import wraps

import config


def login_required(func):
    @wraps(func)  # 可以保留func的一些属性
    def wrapper(*args, **kwargs):
        if config.CMS_USER_ID in session:
            return func(*args, **kwargs)
        else:
            return redirect(url_for("cms.login"))

    return wrapper


def permission_required(permission):
    def outter(func):
        @wraps(func)
        def inner(*args, **kwargs):
            user = g.cms_user
            if user.has_permission(permission):
                return func(*args, **kwargs)
            else:
                # print(url_for("cms.index"))
                return redirect(url_for("cms.index"))
        return inner
    return outter