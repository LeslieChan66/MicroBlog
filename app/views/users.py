import os
import token

from flask import Blueprint,render_template,url_for,request,flash,get_flashed_messages,redirect,current_app
from app.forms import RegisterForm,LoginForm,UploadForm,ChangePasswordForm,ChangeEmailForm,FindPasswordForm,ResetPasswordForm
from app.models import User
from app.exts import db,photos
from app.email import send_mail
from flask_login import login_required,login_user,logout_user,current_user
from PIL import Image
users = Blueprint('users',__name__)


@users.route('/register/',methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        u = User(username=form.username.data,password=form.password.data,email=form.email.data)
        db.session.add(u)
        db.session.commit()
        #生成token  用u对象调用模型中的方法
        token = u.generate_active_token()
        send_mail(u.email,'账户激活','email/activate',username=u.username,token=token)
        flash("恭喜注册成功,请点击邮件中的链接完成激活")
        return redirect(url_for('users.login'))
    return render_template('user/register.html',form=form)

@users.route('/find_password/',methods=['GET','POST'])
def find_password():
    form = FindPasswordForm()
    if not current_user.is_anonymous:                      #不用加登录过后就没有找回密码的按钮
        #验证密码是否为登录状态，如果是，则终止重置密码
        return redirect(url_for('main.index'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            #如果用户存在
            token = user.generate_reset_token()
            #调用User模块中的generate_reset_token函数生成验证信息
            send_mail(form.email.data, '账户激活', 'email/reset_password', username=current_user, token=token)
        flash('重置密码的邮件已经发送，请查收！')
        # return redirect(url_for('user.login'))
    return render_template('user/find_password.html',form=form)

@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm()
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.reset_password(token=token, new_password=form.password.data):
            flash('重设密码成功，请登录')
            return redirect(url_for('users.login'))
        else:
            flash('链接已经失效，请重新获取重设密码链接')
            return redirect(url_for('user.find_password'))
    return render_template('user/reset_password.html', form=form)



#这个方法用来验证token  给用户邮箱发送过去一个完整的url
@users.route('/active/<token>',methods=['GET','POST'])
def active(token):
    if User.check_active_token(token):
        flash("账户激活成功")
        return redirect(url_for('users.login'))
    else:
        flash("账户激活失败")
        return redirect(url_for('main.index'))


@users.route('/login/',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data).first()
        if not u:
            flash("该用户名不存在")
        elif not u.confirmed:
            flash("该账户没有激活,请激活后登录")
        elif u.verify_password(form.password.data):
            login_user(u,remember=form.remember.data)
            flash("登录成功")
            return redirect( request.args.get('next') or url_for("main.index"))
        else:
            flash("密码不正确")
    return render_template('user/login.html',form=form)

@users.route('/logout/',methods=['GET','POST'])
def logout():
    logout_user()
    flash("退出登录成功")
    return redirect(url_for('main.index'))

@users.route('/test/',methods=['GET','POST'])
@login_required
def test():
    return 'this is test'

@users.route('/change_icon/',methods=['GET','POST'])
@login_required
def change_icon():
    img_url = ''
    form = UploadForm()
    if form.validate_on_submit():
        #获取文件后缀
        suffix = os.path.splitext(form.icon.data.filename)[1]
        #随机文件名  拼接
        filename = random_string()+suffix
        photos.save(form.icon.data,name=filename)
        pathname = os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'],filename)
        img = Image.open(pathname)
        img.thumbnail((128,128))
        img.save(pathname)
        if current_user.icon != 'default.jpg':
            os.remove(current_app.config['UPLOADED_PHOTOS_DEST'],current_user.icon)
        current_user.icon = filename #将新上传的文件名 赋值给 用户的头像
        db.session.add(current_user)#保存在数据库中
        flash("头像上传成功")
        return redirect(url_for("users.change_icon"))
    img_url = photos.url(current_user.icon)
    return render_template('user/change_icon.html',form=form,img_url=img_url)

@users.route('/change_password/',methods=['GET','POST'])
@login_required
def change_password():
    form =ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password=form.password.data
            db.session.add(current_user)
            flash('您的密码已经修改！')
            return redirect(url_for('main.index'))
        else:
            flash('原密码错误，操作无效！')
    return render_template('user/change_password.html',form=form)

@users.route('/change_email/',methods=['GET','POST'])
@login_required
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_email(form.old_email.data):
            current_user.email=form.email.data
            db.session.add(current_user)
            flash('您的邮箱已经修改！')
            return redirect(url_for('main.index'))
        else:
            flash('原邮箱错误，操作无效！')
    return render_template('user/change_email.html',form=form)

@users.route('/user_info/', methods=['GET', 'POST'])
@login_required
def user_info():
    return render_template('user/user_info.html')


def random_string(length=20):
    import random
    base_str = 'abc123defhijklmnopqrstuvwxyz4567890'
    return ''.join(random.choice(base_str) for i in range(length))