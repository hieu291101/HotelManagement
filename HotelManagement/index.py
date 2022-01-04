from HotelManagement import app, login
from HotelManagement.admin import *
import utils
from flask_login import login_user
from flask import render_template, request, redirect

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/admin-login', methods=['post'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = utils.check_login(username=username, password=password)
    if user:
        return login_user(user=user)

    return redirect('/admin')

@login.user_loader
def load_user(user_id):
    return utils.get_user_by_id(user_id=user_id)

if __name__ == "__main__":
    app.run(debug=True)