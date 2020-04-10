# @Author:WY
# @Time:2020/2/1021:20
from .models import CMSUser, CMSPermission
from .views import cms
import config
from flask import session, g,render_template



@cms.before_request
def before_request():
    if config.CMS_USER_ID in session:
        user_id = session.get(config.CMS_USER_ID)
        user = CMSUser.query.get(user_id)
        if user:
            g.cms_user = user


@cms.context_processor
def cms_context_processor():
    return {"CMSPermission": CMSPermission}
