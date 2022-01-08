import datetime
from HotelManagement import app, login
from HotelManagement.admin import *
import utils
import cloudinary.uploader
from flask_login import login_user
from flask import render_template, request, redirect, flash, url_for


@app.route('/', methods=["GET", "POST"])
def home():
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
        return redirect('/user-login')

    return render_template('index.html')


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


@app.route('/login-register', methods=['get', 'post'])
def login_register():
    return render_template('login.html')


@app.route('/user-login', methods=['get', 'post'])
def user_login():
    if request.method.__eq__('POST'):
        req = request.form
        username = req.get('username')
        password = req.get('password')

        user = utils.check_login(username=username, password=password)
        if user:
            login_user(user=user)
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


if __name__ == "__main__":
    app.run(debug=True)
