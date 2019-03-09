from app.exts import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask import current_app,flash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, TimedJSONWebSignatureSerializer
from flask_login import UserMixin,AnonymousUserMixin
from app.exts import login_manager
#UserMixin 查看该用户是否登录 以及 是否是匿名用户

class User(UserMixin,db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True,nullable=False)
    username = db.Column(db.String(50),nullable=False,unique=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(128),nullable=False,unique=True)
    confirmed = db.Column(db.Boolean,default=False)
    icon = db.Column(db.String(64),default='default.jpg')
    #lazy 在这里是懒加载 dynamic表示不加载数据但是提供查询
    #如果一对一的关系 需要加上 uselist=Flase
    posts = db.relationship("Posts",backref="user",lazy="dynamic")
    #当前用户通过 user 访问 posts 表中的字段
    #密码不能读 而且永不返回
    @property
    def password(self):
        raise AttributeError("密码不可读的帅哥")

    #设置密码的时候  保存的是加密后的hash值
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    #校验密码是否正确 正确 true 错误 false
    #先加密 再跟数据库比较
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def verify_email(self,email):
        return self.email==email


    #生成token   通过邮箱发送给用户
    def generate_active_token(self,expires_in=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expires_in=expires_in)
        return s.dumps({'id':self.id})
    def reset_password(self, token, new_password):
        """
        :summary: 验证token并重设密码
        :param token:
        :param new_password:
        :return:
        """
        s = TimedJSONWebSignatureSerializer(
            secret_key=current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset_password') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        """
        :summary: 生成重设密码的token
        :param expiration:  token失效时间，单位为秒
        :return:
        """
        s = TimedJSONWebSignatureSerializer(
            secret_key=current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'reset_password': self.id})

    # 验证token 方法
    @staticmethod
    def check_active_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        #这个id是从 token中解析出来的  然后根据id 到数据库中查找  对应的数据进行更新
        u = User.query.get(data.get('id'))
        if not u:
            flash("该用户不存在")
            return False
        if not u.confirmed:
            u.confirmed = True
            db.session.add(u)
        return True

#登录成功以后 执行以下方法 回调函数 获取登录用户的相关信息
@login_manager.user_loader
def load_user(uid):
    return User.query.get(int(uid))
