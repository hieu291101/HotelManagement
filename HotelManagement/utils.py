import datetime
import hashlib

from sqlalchemy import text

from HotelManagement.models import User, Customer, RentalVoucher, OrderVoucher, Room
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
                 gender, address, password, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    name = name.strip()
    username = username.strip()
    customer_type_id = '1' if nationality == "Việt Nam" else '2'
    location_id = '1'
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
                        customer_type_id=customer_type_id,
                        avatar=kwargs.get('avatar'))
    db.session.add(customer)
    db.session.commit()

def load_rental_voucher():
    return db.session.query(Room.room_name, Customer.name, RentalVoucher.check_in_date, RentalVoucher.check_out_date, RentalVoucher.bill_id)\
                     .join(Room, RentalVoucher.room_id.__eq__(Room.id))\
                     .join(Customer, RentalVoucher.customer_id.__eq__(Customer.id)).all()
# def load_income():
#     return  db.session.query(Room.room_name, Customer.name, RentalVoucher.check_in_date, RentalVoucher.check_out_date, RentalVoucher.bill_id,
#                                    Bill.unit_price, Surchange.surchange)\
#                      .join(Room, RentalVoucher.room_id.__eq__(Room.id))\
#                      .join(Customer, RentalVoucher.customer_id.__eq__(Customer.id)).all()

def load_rental_voucher_by(customer_name=None):
    rental_voucher = db.session.query(Room.room_name, Customer.id_number, Customer.name, RentalVoucher.check_in_date, RentalVoucher.check_out_date, RentalVoucher.bill_id)\
                     .join(Room, RentalVoucher.room_id.__eq__(Room.id))\
                     .join(Customer, RentalVoucher.customer_id.__eq__(Customer.id))
    if customer_name:
        rental_voucher = rental_voucher.filter(Customer.name.contains(customer_name))

    return rental_voucher

def load_room_left():
   return db.engine.execute(text("SELECT id FROM room WHERE id not in (SELECT room_id FROM rental_voucher)")).all()


