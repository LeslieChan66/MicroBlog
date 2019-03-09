from flask import Blueprint,render_template,request,flash,get_flashed_messages,redirect,current_app,url_for
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app.models import Posts
from app.forms import PostForm
from flask_login import current_user
from app.exts import db



main = Blueprint('main',__name__)
@main.route('/',methods=['GET','POST'])
def index():
    form = PostForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:#如果登录
            #获取当前用户
            u = current_user._get_current_object()
            p = Posts(content=form.content.data,user=u)
            db.session.add(p)
            return redirect(url_for('main.index'))
        else:
            flash("请先登录")
            return redirect(url_for('users.login'))
    #调取所有发表的博客
    # posts = Posts.query.filter_by(rid=0).all()
    #www.baidu.com?page=1
    #接收用户 url传递过来的 page参数
    page = request.args.get('page',1,type=int)
    pagination = Posts.query.filter_by(rid=0).order_by(Posts.timestamp.desc()).paginate(page,per_page=5,error_out=False)
    posts = pagination.items
    return render_template('main/index.html',form=form,posts=posts,pagination=pagination)

# @main.route('/token/',methods=['GET','POST'])
# def token():
#     s = Serializer(current_app.config['SECRET_KEY'],expires_in=3600)
#     return s.dumps({'id':666})
#
# @main.route('/check/',methods=['GET','POST'])
# def check():
#     t = 'eyJhbGciOiJIUzUxMiIsImlhdCI6MTU0NzUzNzQ2OCwiZXhwIjoxNTQ3NTQxMDY4fQ.eyJpZCI6NjY2fQ.oVWgGFIS9ew0pZrzqk-5RetoUSBuPeimbMN4E7R1hveFhC3BAQlOSy-IH-0lBH7GnkaDvf2fasAMKmFCci4HiA'
#     s = Serializer(current_app.config['SECRET_KEY'])
#     data = s.loads(t)
#     return str(data['id'])