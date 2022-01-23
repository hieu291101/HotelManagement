import datetime
import hashlib
import math

import cloudinary.uploader
from flask import render_template, request, redirect, flash, url_for, session, jsonify
from flask_login import login_user

from HotelManagement import app, login, bcrypt, utils
from HotelManagement.admin import *

##########
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_mail import Mail, Message
from threading import Thread
from itsdangerous import URLSafeTimedSerializer
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from flask_bcrypt import Bcrypt
from datetime import datetime


# from forms import RegisterForm, LoginForm, ResetEmailForm, ResetPasswordForm


@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        req = request.form
        checkindate = req.get('checkindate')
        checkoutdate = req.get('checkoutdate')
        adults = req.get('adults')

        session['checkindate'] = checkindate
        session['checkoutdate'] = checkoutdate
        session['adults'] = adults

        # Kiểm tra nhập đủ giá trị hay chưa
        if checkindate and checkoutdate and adults:
            checkindatetime = datetime.datetime.strptime(checkindate, "%Y-%m-%d")
            checkoutdatetime = datetime.datetime.strptime(checkindate, "%Y-%m-%d")
            check_dates = utils.check_date(datetime.datetime.now(), checkindatetime)
        else:
            flash('Chưa nhập đủ giá trị', 'danger')
            return redirect(request.url)

        # Kiểm tra các ràng buộc
        if not check_dates:
            flash('Thời điểm nhận phòng không quá 28 ngày kể từ thời điểm đặt phòng', "warning")
            return redirect(request.url)
        elif checkindatetime < datetime.datetime.now() and (checkindatetime - checkoutdatetime).days == 0:
            flash('Thời điểm nhận phòng hoặc thời điểm trả phòng không hợp lệ', "error")
            return redirect(request.url)
        return redirect('/order')

    return render_template('index.html')


# user
@app.route('/user-register', methods=['get', 'post'])
def user_register():
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        identity = request.form.get('identity')
        nationality = request.form.get('nationality')
        gender = request.form.get('gender')
        address = request.form.get('address')
        password = request.form.get('password')
        confirmpassword = request.form.get('confirmpassword')
        avatar_path = None

        try:
            if password.strip().__eq__(confirmpassword.strip()):
                avatar = request.files.get('avatar')
                if avatar:
                    respose = cloudinary.uploader.upload(avatar)
                    avatar_path = respose['secure_url']

                utils.add_customer(name=name,
                                   username=username,
                                   email=email,
                                   phone=phone,
                                   identity=identity,
                                   nationality=nationality,
                                   gender=gender,
                                   address=address,
                                   password=password,
                                   avatar=avatar_path)
                flash('Đăng ký thành công', 'success')
                return redirect(url_for('user_login'))
            else:
                flash('Mật khẩu không khớp', 'error')
        except:
            flash('Hệ thống đang có lỗi !!', 'error')
    return render_template('register.html')


@app.route('/user-login', methods=['get', 'post'])
def user_login():
    if current_user.is_authenticated:
        return redirect('/user-pagination')

    if request.method.__eq__('POST'):
        req = request.form
        username = req.get('username')
        password = req.get('password')

        user = utils.check_login(username=username, password=password)
        if user:
            login_user(user=user)
            return redirect('/user-pagination')
        else:
            flash('Tài khoản hoặc mật khầu không khả dụng', 'error')
            return redirect(request.url)

    return render_template('login.html')


@app.route('/user-logout')
def user_logout():
    logout_user()
    return redirect(url_for('user_login'))


@app.route('/user-pagination')
def user_pagination():
    if current_user.type == 'administrator':
        return redirect('/admin')
    elif current_user.type == 'staff':
        return redirect('/staff-page')
    else:
        return redirect('/')


@login.user_loader
def load_user(user_id):
    return utils.get_user_by_id(user_id=user_id)


# admin - staff
@app.route('/admin-login', methods=['post'])
def admin_login():
    req = request.form
    username = req.get('username')
    password = req.get('password')

    user = utils.check_login(username=username, password=password)
    if user:
        login_user(user=user)

    return redirect('/admin')


@app.route('/staff-page')
def staff_page():
    if not current_user.is_authenticated and current_user.type == 'staff':
        return redirect('/user-login')

    room_name = request.args.get('roomname')
    customer_name = request.args.get('customername')
    keyword = request.args.get('keyword')
    page = request.args.get('page', 1)
    cmnd = request.args.get('cmnd')

    counter = utils.count_rental_vouchers()
    rental_voucher_by = utils.load_rental_voucher_by(customer_name=keyword, page=int(page))
    customer = utils.load_customer_for_rental(room_name=room_name, customer_name=customer_name)

    return render_template('staff.html',
                           rental_voucher=utils.load_rental_voucher(), room_left=utils.load_room_left(),
                           rental_voucher_by=rental_voucher_by, pages=math.ceil(counter / app.config['PAGE_SIZE']),
                           customer=customer)


@app.route('/staff-page/order')
def staff_page_order():
    if not current_user.is_authenticated and current_user.type == 'staff':
        return redirect('/user-login')

    keyword = request.args.get('keyword')
    page = request.args.get('page', 1)

    counter = utils.count_order_vouchers()
    order_voucher_by = utils.load_order_voucher_by(customer_name=keyword, page=int(page))

    return render_template('staff_order.html', order_voucher=utils.load_order_voucher(),
                           order_voucher_by=order_voucher_by,
                           pages=math.ceil(counter / app.config['PAGE_SIZE']))


@app.route('/order', methods=["GET", "POST"])
def order_room():
    if request.method == "POST":
        req = request.form
        checkindate = req.get('checkindate')
        checkoutdate = req.get('checkoutdate')
        adults = req.get('adults')

        # Kiểm tra nhập đủ giá trị hay chưa
        if checkindate and checkoutdate and adults:
            checkindatetime = datetime.datetime.strptime(checkindate, "%Y-%m-%d")
            checkoutdatetime = datetime.datetime.strptime(checkindate, "%Y-%m-%d")
            check_dates = utils.check_date(datetime.datetime.now(), checkindatetime)
        else:
            flash('Chưa nhập đủ giá trị', 'danger')
            return redirect(request.url)

        # Kiểm tra các ràng buộc
        if not check_dates:
            flash('Thời điểm nhận phòng không quá 28 ngày kể từ thời điểm đặt phòng', "warning")
            return redirect(request.url)
        elif checkindatetime < datetime.datetime.now() and (checkindatetime - checkoutdatetime).days == 0:
            flash('Thời điểm nhận phòng hoặc thời điểm trả phòng không hợp lệ', "warning")
            return redirect(request.url)

        session['checkindate'] = checkindate
        session['checkoutdate'] = checkoutdate
        session['adults'] = adults

    page = request.args.get('page', 1)

    counter = utils.count_room_type()
    load_room_type = utils.load_room_type(page=page)

    return render_template('order.html', load_room_type=load_room_type,
                           pages=math.ceil(counter / app.config['PAGE_SIZE']))


# handle
@app.context_processor
def utility_processor():
    def count_room_by_room_type(roomtype):
        counter_room_full = utils.count_room_full_by(from_date=session['checkindate'], to_date=session['checkoutdate'],
                                                     room_type=roomtype)
        counter = utils.count_room_empty(room_type=roomtype)
        return counter - counter_room_full

    return dict(count_room_by_room_type=count_room_by_room_type, order_stats=utils.count_order(session.get('order')))


@app.route('/api/add-order', methods=['post'])
def add_to_order():
    data = request.json
    id = str(data.get('id'))
    room_type_name = data.get('room_type_name')
    capacity = data.get('capacity')
    price = data.get('price')

    order = session.get('order')
    if not order:
        order = {}

    if id in order:
        order[id]['quantity'] = order[id]['quantity'] + 1
    else:
        order[id] = {
            'id': id,
            'room_type_name': room_type_name,
            'capacity': capacity,
            'price': price,
            'quantity': 1
        }

    session['order'] = order

    return jsonify(utils.count_order(order))


# @app.route('/api/add-staff-order', methods=['post'])
# def add_to_order():
#     data = request.json
#     id=str(data.get('id'))
#     room_type_name=data.get('room_type_name')
#     capacity=data.get('capacity')
#     price=data.get('price')
#
#     order = session.get('staff-order')
#     if not order:
#         order={}
#
#     if id in order:
#         order[id]['quantity'] = order[id]['quantity'] + 1
#     else:
#         order[id] = {
#             'id': id,
#             'room_type_name': room_type_name,
#             'capacity': capacity,
#             'price': price,
#             'quantity': 1
#         }
#
#     session['order'] = order

@app.route('/order-detail')
def order_detail():
    return render_template('order_detail.html',
                           stats=utils.count_order(session['order']))


# @app.route('/api/pay', methods=['post'])
# def pay():
#     try
#     uti
#     except:
#         return jsonify({'code', 200})
#
#     return jsonify({'code': 404})


# reset_email password route
@app.route('/password_reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'GET':
        return render_template('reset_password.html')

    if request.method == 'POST':
        email = request.form.get('email')
        customer = Customer.verify_email(email)

        if customer:
            utils.send_email(customer)
            flash("Chúng tôi vừa gửi mã xác nhận đến email, vui lòng kiểm trả email !", "success")

        return redirect(url_for('user_login'))


@app.route('/password_reset_verified/<token>', methods=['GET', 'POST'])
def reset_verified(token):
    user = utils.verify_reset_token(token)

    if not user:
        print('no user found')
        return redirect(url_for('user_login'))

    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirmpassword = request.form.get('confirmpassword')

        try:
            if password.strip().__eq__(confirmpassword.strip()):
                user.set_password(password)
                flash("Thay đổi mật khẩu thành công!!!", "success")
                return redirect(url_for('user_login'))
            else:
                flash('Mật khẩu và mật khẩu xác nhận không khớp!!!', 'error')
                return redirect(request.url)
        except:
            flash('Hệ thống đang có lỗi !!', 'error')

    return render_template('reset_verified.html')


if __name__ == "__main__":
    app.run(debug=True)
