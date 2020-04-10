# @Author:WY
# @Time:2020/2/1016:45
from io import BytesIO
from flask import (
    Blueprint,
    views,
    render_template,
    request,
    session,
    make_response, url_for, g, abort)
from sqlalchemy import func

from .forms import SignupForm, SigninForm, AddPostForm, AddCommentForm
from utils import zlcache, safeutils
from utils.captcha import Captcha
from utils import restful
from .models import FrontUser
from exts import db
import config
from ..cms.decorators import permission_required
from ..cms.models import CMSPermission
from ..models import BannerModel, BoardModel, PostModel, CommentModel, HighlightPostModel
from .decorators import login_required
from flask_paginate import Pagination, get_page_parameter

front = Blueprint("front", __name__)


@front.route("/captcha/")
def graph_captcha():
    text, image = Captcha.gene_graph_captcha()
    zlcache.set(text.lower(), text.lower())
    out = BytesIO()
    image.save(out, "png")
    out.seek(0)
    resp = make_response(out.read())
    resp.content_type = "image/png"
    return resp


@front.route("/")
def index():
    board_id = request.args.get("bd", type=int, default=None)
    sort = request.args.get("st", type=int, default=1)
    query_obj = None
    if sort == 1:
        query_obj = PostModel.query.order_by(PostModel.create_time.desc())
    elif sort == 2:
        # 按照加精的事件倒序排序
        query_obj = db.session.query(PostModel).outerjoin(HighlightPostModel).order_by(
            HighlightPostModel.create_time.desc(), PostModel.create_time.desc())  # 加精用加精的时间排序,未加精用未加精的事件排序
    elif sort == 3:
        # 按照点赞的数量排序
        query_obj = PostModel.query.order_by(PostModel.create_time.desc())
    elif sort == 4:
        # 评论数量排序
        query_obj = db.session.query(PostModel).outerjoin(CommentModel).group_by(PostModel.id).order_by(
            func.count(CommentModel.id).desc(), PostModel.create_time.desc())
    page = request.args.get(get_page_parameter(), type=int, default=1)
    banners = BannerModel.query.order_by(BannerModel.priority.desc()).limit(4)
    boards = BoardModel.query.all()
    start = (page - 1) * config.PER_PAGE
    end = start + config.PER_PAGE
    posts = None
    total = 0
    if board_id:
        query_obj = query_obj.filter(PostModel.board_id==board_id)
        posts = query_obj.slice(start, end)
        total = query_obj.count()
    else:
        posts = query_obj.slice(start, end)
        total = PostModel.query.count()
    pagination = Pagination(bs_version=3, page=page, total=total, outer_window=0, inner_window=2)
    context = {
        "banners": banners,
        "boards": boards,
        "posts": posts,
        "pagination": pagination,
        "current_board": board_id,
        "current_sort": sort
    }
    return render_template("front/front_index.html", **context)


@front.route("/apost/", methods=["GET", "POST"])
@login_required
def apost():
    if request.method == "GET":
        boards = BoardModel.query.all()
        return render_template("front/front_apost.html", boards=boards)
    else:
        form = AddPostForm(request.form)
        if form.validate():
            title = form.title.data
            content = form.content.data
            board_id = form.board_id.data
            board = BoardModel.query.get(board_id)
            if not board:
                return restful.params_error(message="没有这个板块!")
            else:
                post = PostModel(title=title, content=content)
                post.board = board
                post.author = g.front_user
                db.session.add(post)
                db.session.commit()
                return restful.success()
            return restful.params_error(message=form.get_error())


@front.route("/p/<post_id>/")
def post_detail(post_id):
    post = PostModel.query.get(post_id)
    if not post_id:
        abort(404)
    return render_template("front/front_pdetail.html", post=post)


@front.route("/acomment/", methods=["POST"])
@login_required
def add_comment():
    form = AddCommentForm(request.form)
    if form.validate():
        content = form.content.data
        post_id = form.post_id.data
        post = PostModel.query.get(post_id)
        if post:
            comment = CommentModel(content=content)
            comment.post = post
            comment.author = g.front_user
            db.session.add(comment)
            db.session.commit()
            return restful.success()
        else:
            return restful.params_error(message="没有这篇帖子!")
    else:
        return restful.params_error(form.get_error())


class SignupView(views.MethodView):
    def get(self):
        return_to = request.referrer
        if return_to and return_to != request.url and safeutils.is_safe_url(return_to):
            return render_template("front/front_signup.html", return_to=return_to)
        else:
            return render_template("front/front_signup.html")

    def post(self):
        print("signup form post")
        form = SignupForm(request.form)
        if form.validate():
            telephone = form.telephone.data
            username = form.username.data
            password = form.password1.data
            user = FrontUser(telephone=telephone, username=username, password=password)
            db.session.add(user)
            db.session.commit()
            return restful.success()
        else:
            # print("form.get_error()", form.get_error())
            return restful.params_error(message=form.get_error())


class SigninView(views.MethodView):
    def get(self):
        return_to = request.referrer
        if return_to and return_to != request.url and return_to != url_for("front.signup") and safeutils.is_safe_url(
                return_to):
            return render_template("front/front_signin.html", return_to=return_to)
        else:
            return render_template("front/front_signin.html")

    def post(self):
        form = SigninForm(request.form)
        if form.validate():
            telephone = form.telephone.data
            password = form.password.data
            remember = form.remeber.data
            user = FrontUser.query.filter_by(telephone=telephone).first()
            if user and user.check_password(password):
                session[config.FRONT_USER_ID] = user.id
                if remember:
                    session.permanent = True
                print("success")
                return restful.success()
            else:
                return restful.params_error(message="手机号码或者密码错误")
        else:
            return restful.params_error(message=form.get_error())


front.add_url_rule("/signup/", view_func=SignupView.as_view("signup"))
front.add_url_rule("/signin/", view_func=SigninView.as_view("signin"))
