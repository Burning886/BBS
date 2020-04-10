# @Author:WY
# @Time:2020/2/1016:44
from sqlalchemy.orm import relationship

from exts import db
from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class CMSPermission:
    # 255的二进制方式来表示1111 1111
    ALL_PERMISSION = 0b11111111
    # 1. 访问者权限
    VISITOR = 0b00000001
    # 2. 管理帖子
    POSTER = 0b00000010
    # 3. 管理评论权限
    COMMENTER = 0b00000100
    # 4. 管理板块权限
    BOARDER = 0b00001000
    # 5. 管理前台用户的权限
    FRONTUSER = 0b00010000
    # 6. 管理后台用户的权限
    CMSUSER = 0b00100000
    # 7. 管理后台管理员权限
    ADMIN = 0b01000000


cms_role_user = db.Table(
    "cms_role_user",
    Column("cms_role_id", Integer, ForeignKey("cms_role.id"), primary_key=True),
    Column("cms_user_id", Integer, ForeignKey("cms_user.id"), primary_key=True)
)


class CMSRole(db.Model):
    __tablename__ = "cms_role"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    desc = Column(String(200), nullable=True)
    create_time = Column(DateTime, default=datetime.now)
    permissions = Column(Integer, default=CMSPermission.VISITOR)
    users = relationship("CMSUser", secondary=cms_role_user, backref="roles")


class CMSUser(db.Model):
    __tablename__ = "cms_user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False)
    _password = Column("password", String(100), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    join_time = Column(DateTime, default=datetime.now)

    # 没有构造方法的话:user = CMSUser(username=username, password=password, email=email)
    def __int__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw_password):
        self._password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        result = check_password_hash(self.password, raw_password)
        return result

    @property
    def permmissions(self):
        if not self.roles:
            return 0
        all_permissions = 0
        for role in self.roles:
            permissions = role.permissions
            all_permissions |= permissions
        return all_permissions

    def has_permission(self, permission):
        all_permissions = self.permmissions
        result = all_permissions & permission == permission
        return result

    @property
    def is_developer(self):
        return self.has_permission(CMSPermission.ALL_PERMISSION)
