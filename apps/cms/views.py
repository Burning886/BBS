# @Author:WY
# @Time:2020/2/1016:44
import random
import string

from flask import Blueprint, views, render_template, request, session, redirect, url_for, g

from exts import db, mail
from utils import restful
from .forms import LoginForm, ResetpwdForm, AddBannerForm, UpdateBannerForm, AddBoardForm, UpdateBoardForm
from .models import CMSUser, CMSPermission
from .decorators import login_required, permission_required
import config
from flask_mail import Message
from ..models import BannerModel, BoardModel, PostModel, HighlightPostModel
from flask_paginate import Pagination, get_page_parameter

cms = Blueprint("cms", __name__, url_prefix="/cms")


@cms.route("/")
@login_required
def index():
    # g.cms_user
    return render_template("cms/cms_index.html")


@cms.route("/posts/")
@login_required
@permission_required(CMSPermission.POSTER)
def posts():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * config.PER_PAGE
    end = start + config.PER_PAGE
    posts = None
    total = 0
    # posts = PostModel.query.slice(start, end)
    # total = PostModel.query.count()
    pagination = Pagination(bs_version=3, page=page, total=total, outer_window=0, inner_window=2)
    context = {
        "posts": PostModel.query.all(),
        "pagination": pagination,
    }
    return render_template("cms/cms_posts.html", **context)


@cms.route("/hpost/", methods=["POST"])
@login_required
@permission_required(CMSPermission.POSTER)
def hpost():
    post_id = request.form.get("post_id")
    if not post_id:
        return restful.params_error("请传入帖子id!")
    post = PostModel.query.get(post_id)
    if not post:
        return restful.params_error("没有这篇帖子")
    highlight = HighlightPostModel()
    highlight.post = post
    db.session.add(highlight)
    db.session.commit()
    return restful.success()


@cms.route("/uhpost/", methods=["POST"])
@login_required
@permission_required(CMSPermission.POSTER)
def uhpost():
    post_id = request.form.get("post_id")
    if not post_id:
        return restful.params_error("请传入帖子id!")
    post = PostModel.query.get(post_id)
    if not post:
        return restful.params_error("没有这篇帖子")
    highlight = HighlightPostModel.query.filter_by(post_id=post_id).first()
    db.session.delete(highlight)
    db.session.commit()
    return restful.success()


@cms.route("/comments/")
@login_required
@permission_required(CMSPermission.COMMENTER)
def comments():
    return render_template("cms/cms_comments.html")


@cms.route("/boards/")
@login_required
@permission_required(CMSPermission.BOARDER)
def boards():
    board_models = BoardModel.query.all()
    context = {
        "boards": board_models
    }
    return render_template("cms/cms_boards.html", **context)


@cms.route("/aboard/", methods=["POST"])
@login_required
@permission_required(CMSPermission.BOARDER)
def aboard():
    form = AddBoardForm(request.form)
    if form.validate():
        name = form.name.data
        board = BoardModel(name=name)
        db.session.add(board)
        db.session.commit()
        return restful.success()
    else:
        return restful.params_error(message=form.get_error())


@cms.route('/uboard/', methods=['POST'])
@login_required
@permission_required(CMSPermission.BOARDER)
def uboard():
    form = UpdateBoardForm(request.form)
    if form.validate():
        board_id = form.board_id.data
        name = form.name.data
        board = BoardModel.query.get(board_id)
        if board:
            board.name = name
            db.session.commit()
            return restful.success()
        else:
            return restful.params_error(message='没有这个板块！')
    else:
        return restful.params_error(message=form.get_error())


@cms.route('/dboard/', methods=['POST'])
@login_required
@permission_required(CMSPermission.BOARDER)
def dboard():
    board_id = request.form.get("board_id")
    if not board_id:
        return restful.params_error('请传入板块id！')

    board = BoardModel.query.get(board_id)
    if not board:
        return restful.params_error(message='没有这个板块！')

    db.session.delete(board)
    db.session.commit()
    return restful.success()


@cms.route("/fusers/")
@login_required
@permission_required(CMSPermission.FRONTUSER)
def fusers():
    return render_template("cms/cms_fusers.html")


@cms.route("/cusers/")
@login_required
@permission_required(CMSPermission.CMSUSER)
def cusers():
    return render_template("cms/cms_cusers.html")


@cms.route("/croles/")
@login_required
@permission_required(CMSPermission.ALL_PERMISSION)
def croles():
    return render_template("cms/cms_croles.html")


class LoginView(views.MethodView):
    def get(self, message=None):
        return render_template("cms/cms_login.html", message=message)

    def post(self):
        form = LoginForm(request.form)
        if form.validate():
            email = form.email.data
            password = form.password.data
            remember = form.remember.data
            user = CMSUser.query.filter_by(email=email).first()
            if user and user.check_password(password):
                session[config.CMS_USER_ID] = user.id
                if remember:
                    session.permanent = True  # 默认31天
                return redirect(url_for("cms.index"))
            else:
                return self.get(message="用户不存在")
        else:
            print(form.errors)
            message = form.get_error()
            # print(form.errors)
            # print(form.errors.popitem())
            return self.get(message=message)


@cms.route("/logout/")
@login_required
def logout():
    del session[config.CMS_USER_ID]
    return redirect(url_for("cms.login"))


@cms.route("/profile/")
@login_required
def profile():
    return render_template("cms/cms_profile.html")


@cms.route("/abanner/", methods=["POST"])
@login_required
def abanner():
    form = AddBannerForm(request.form)
    if form.validate():
        name = form.name.data
        image_url = form.image_url.data
        link_url = form.link_url.data
        priority = form.priority.data
        banner = BannerModel(name=name, image_url=image_url, link_url=link_url, priority=priority)
        db.session.add(banner)
        db.session.commit()
        return restful.success()
    else:
        return restful.params_error(message=form.get_error())


@cms.route("/ubanner/", methods=["POST"])
@login_required
def ubanner():
    form = UpdateBannerForm(request.form)
    if form.validate():
        banner_id = form.banner_id.data
        name = form.name.data
        image_url = form.image_url.data
        link_url = form.link_url.data
        priority = form.priority.data
        banner = BannerModel.query.get(banner_id)
        if banner:
            banner.name = name
            banner.image_url = image_url
            banner.link_url = link_url
            banner.priority = priority
            db.session.commit()
            return restful.success()
        else:
            return restful.params_error(message="没有这个轮播图!")
    else:
        return restful.params_error(message=form.get_error())


@cms.route("/dbanner/", methods=["POST"])
@login_required
def dbanner():
    banner_id = request.form.get("banner_id")
    if not banner_id:
        return restful.params_error(message="请传入轮播图id")
    banner = BannerModel.query.get(banner_id)
    if not banner:
        return restful.params_error(message="没有这个轮播图")
    db.session.delete(banner)
    db.session.commit()
    return restful.success()


@cms.route("/banners/")
@login_required
def banners():
    banners = BannerModel.query.order_by(BannerModel.priority.desc()).all()
    return render_template("cms/cms_banners.html", banners=banners)


class ResetPwdView(views.MethodView):
    decorators = [login_required]

    def get(self):
        print("get")
        return render_template("cms/cms_resetpwd.html")

    def post(self):
        print("post")
        form = ResetpwdForm(request.form)
        if form.validate():
            oldpwd = form.oldpwd.data
            newpwd = form.newpwd.data
            user = g.cms_user
            if user.check_password(oldpwd):
                user.password = newpwd
                db.session.commit()
                return restful.success()
            else:
                return restful.params_error("旧密码错误")
        else:
            message = form.get_error()
            return restful.params_error(message)


class ResetEmailView(views.MethodView):
    def get(self):
        return render_template("cms/cms_resetemail.html")

    def post(self):
        pass


@cms.route("/email/")
def sendemail():
    message = Message('恭喜你中了一百万', recipients=['1764792621@qq.com'], body="邵良森大傻B")
    mail.send(message)
    return "邮件发送成功"


@cms.route("/email_captcha/")
def email_captcha():
    email = request.args.get("email")
    if email:
        return restful.params_error("请传递邮箱参数!")
    source = list(string.ascii_letters)
    # source.extend(["1","2","3","4","5","6","7","8","8"])
    source.extend(map(lambda x: str(x), range(0, 10)))
    captcha = "".join(random.sample(source, 6))
    message = Message("维奈斯CMS验证码", recipients=[email], body="验证码是:%s" % captcha)
    try:
        mail.send(message)
    except:
        return restful.server_error()
    return restful.success()


cms.add_url_rule("/login/", view_func=LoginView.as_view("login"))
cms.add_url_rule("/resetpwd/", view_func=ResetPwdView.as_view("resetpwd"), methods=["GET", "POST"])
cms.add_url_rule('/resetemail/', view_func=ResetEmailView.as_view("resetemail"))
