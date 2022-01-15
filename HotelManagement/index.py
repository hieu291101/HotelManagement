import datetime
import math

from sqlalchemy import null

from HotelManagement import app, login
from HotelManagement.admin import *
import utils
import cloudinary.uploader
from flask_login import login_user
from flask import render_template, request, redirect, flash, url_for, session, jsonify


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
            flash('Thời điểm nhận phòng hoặc thời điểm trả phòng không hợp lệ', "warning")
            return redirect(request.url)
        return redirect('/order')

    return render_template('index.html')

@app.route('/order', methods=["GET", "POST"])
def order_room():

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
            flash('Thời điểm nhận phòng hoặc thời điểm trả phòng không hợp lệ', "warning")
            return redirect(request.url)

    page = request.args.get('page', 1)
    check_in_date = session['checkindate']
    check_out_date = session['checkoutdate']

    counter = utils.count_room_empty()
    load_room_empty = utils.load_room_empty(from_date=check_in_date, to_date=check_out_date, page=page)

    return render_template('order.html', load_room_empty=load_room_empty,
                           pages=math.ceil(counter / app.config['PAGE_SIZE']))


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
                flash('Mật khẩu không khớp', 'warning')
        except:
            flash('Hệ thống đang có lỗi !!', 'warning')
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
            flash('Tài khoản hoặc mật khầu không khả dụng', 'warning')
            return redirect(request.url)

    return render_template('login.html')


@app.route('/user-logout')
def user_logout():
    logout_user()
    return redirect(url_for('user_login'))


@app.route('/admin-login', methods=['post'])
def admin_login():
    req = request.form
    username = req.get('username')
    password = req.get('password')

    user = utils.check_login(username=username, password=password)
    if user:
        login_user(user=user)

    return redirect('/admin')


@login.user_loader
def load_user(user_id):
    return utils.get_user_by_id(user_id=user_id)


@app.route('/user-pagination')
def user_pagination():
    if current_user.type == 'administrator':
        return redirect('admin')
    elif current_user.type == 'staff':
        return redirect('/staff-page')
    else:
        return redirect('/')


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

    return render_template('staff_order.html',order_voucher=utils.load_order_voucher(),
                           order_voucher_by=order_voucher_by,
                           pages=math.ceil(counter / app.config['PAGE_SIZE']))

@app.route('/api/add-order', methods=['post'])
def add_to_order():
    check_in_date=''
    check_out_date=''
    people=''

    order = session.get('order')
    if not order:
        order={}

    order= {
        'check_in_date': check_in_date,
        'check_out_date': check_out_date,
        'people': people
    }

    session['order'] = order

    return jsonify()

if __name__ == "__main__":
    app.run(debug=True)
