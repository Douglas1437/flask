from flask import Blueprint, make_response, session, jsonify
from flask import current_app
from flask import request
from models import db,UserInfo

user_blueprint = Blueprint('user', __name__, url_prefix='/user')


@user_blueprint.route('/image_yzm')
def image_yzm():
    from utils.captcha.captcha import captcha
    # name表示一个随机的名称
    # yzm表示验证码字符串
    # buffer文件的二进制数据
    name, yzm, buffer = captcha.generate_captcha()

    # 将验证码字符串存入session中，用于后续请求时进行对比
    session['image_yzm'] = yzm

    response = make_response(buffer)
    # 默认返回的内容会被当作text/html解析，如下代码告诉浏览器解释为图片
    response.mimetype = 'image/png'

    return response


@user_blueprint.route('/sms_yzm')
def sms_yzm():
    # 获取数据：手机号，图片验证码
    dict1 = request.args
    mobile = dict1.get('mobile')
    image_yzm = dict1.get('image_yzm')

    # 对比图片验证码
    if image_yzm != session['image_yzm']:
        return jsonify(result=1)

    # 判断手机号是否已经存在

    # 随机生成一个数字（4位）
    import random
    yzm = random.randint(1000, 9999)

    # 保存到session
    session['sms_yzm'] = yzm

    from utils.ytx_sdk import ytx_send
    # ytx_send.sendTemplateSMS(mobile,{yzm,5},1)
    print(yzm)

    return jsonify(result=2)


@user_blueprint.route('/register', methods=['POST'])
def register():
    # 1.接收数据
    dict1 = request.form
    mobile = dict1.get('mobile')
    image_yzm = dict1.get('image_yzm')
    sms_yzm = dict1.get('sms_yzm')
    pwd = dict1.get('pwd')

    # 2.验证数据的有效性
    # 判断所有数据是否存在
    if not all([mobile, image_yzm, sms_yzm, pwd]):
        return jsonify(result=1)
    # 判断图片验证码是否正确
    if image_yzm != session['image_yzm']:
        return jsonify(result=2)
    # 判断短信验证码是否正确
    if int(sms_yzm) != session['sms_yzm']:
        return jsonify(result=3)
    # 判断密码的长度
    import re
    if not re.match(r'[a-zA-Z0-9_]{6,20}', pwd):
        return jsonify(result=4)
    # 判断手机号是否存在
    mobile_count = UserInfo.query.filter_by(mobile=mobile).count()
    if mobile_count > 0:
        return jsonify(result=5)

    # 3.创建对象
    user = UserInfo()
    user.nick_name = mobile
    user.mobile = mobile
    user.password = pwd

    # 4.提交
    try:
        db.session.add(user)
        db.session.commit()
    except:
        current_app.logger_xjzx.error('注册用户时数据库访问失败')
        return jsonify(result=6)

    # 返回响应
    return jsonify(result=7)

@user_blueprint.route('/login',methods=['POST'])
def login():
    #接收
    dict1=request.form
    mobile=dict1.get('mobile')
    pwd=dict1.get('pwd')

    #验证
    if not all([mobile,pwd]):
        return jsonify(result=1)

    #处理：查询select * from user_info where ... limit 0,1
    user=UserInfo.query.filter_by(mobile=mobile).first()
    #如果mobile存在则返回对象，不存在则返回None
    if user:
        #判断密码是否正确
        if user.check_pwd(pwd):
            #登录成功
            #进行状态保持
            session['user_id']=user.id
            #将头像、昵称称回给浏览器显示
            return jsonify(result=3,avatar=user.avatar,nick_name=user.nick_name)
        else:
            #密码错误
            return jsonify(result=4)
    else:
        #提示mobile错误
        return jsonify(result=2)

@user_blueprint.route('/logout',methods=['POST'])
def logout():
    session.pop('user_id')
    return jsonify(result=1)

@user_blueprint.route('/show')
def show():
    if 'user_id' in session:
        return 'ok'
    else:
        return 'no'
