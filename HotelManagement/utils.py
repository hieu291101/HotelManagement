import datetime
import hashlib

from HotelManagement.models import User, db, Customer


def get_user_by_id(user_id):
    return User.query.get(user_id)


def check_login(username, password):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        return User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password)).first()


def check_date(orderdate, checkindate):
    if checkindate and orderdate:
        delta = checkindate - orderdate

        if delta.days > 28:
            return False

    return True


def add_customer(name, username, email, phone, identity, nationality,
                 gender, address, password, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    customer = Customer(name=name.strip(),
                        email=email,
                        phone=phone,
                        identity=identity,
                        nationality=nationality,
                        gender=gender,
                        address=address)
    user = User(username=username.strip(), password=password, type='customer')

    db.session.add(customer)
    db.session.add(user)
    db.session.commit()
