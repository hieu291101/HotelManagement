import datetime
import hashlib

from HotelManagement.models import User, Customer
from HotelManagement import db


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
                 gender, address, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    name = name.strip()
    username = username.strip()
    customer_type_id = '1' if nationality == "Việt Nam" else '2'
    location_id = '1'
    print('ss')
    customer = Customer(name=name,
                        gender=gender,
                        email=email,
                        id_number=identity,
                        nationality=nationality,
                        address=address,
                        phone_number=phone,
                        username=username,
                        password=password,
                        location_id=location_id,
                        customer_type_id=customer_type_id)
    print('ss')
    db.session.add(customer)
    print('ss')
    db.session.commit()
