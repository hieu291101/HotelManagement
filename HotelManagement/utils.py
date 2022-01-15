import datetime
import hashlib

from sqlalchemy import text

from HotelManagement.models import User, Customer, RentalVoucher, OrderVoucher, Room, Bill, Surchange, CustomerType, \
    RoomType
from HotelManagement import db, app


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

def load_income():
    income =  db.session.query(Room.room_name, Customer.id_number, Customer.name, RentalVoucher.check_in_date, RentalVoucher.check_out_date,
                                   Bill.unit_price, Bill.status, Surchange.surchange)\
                     .join(Room, RentalVoucher.room_id.__eq__(Room.id))\
                     .join(Customer, RentalVoucher.customer_id.__eq__(Customer.id))\
                     .join(Bill, RentalVoucher.bill_id.__eq__(Bill.id))\
                     .join(Surchange, Surchange.id.__eq__(Bill.surchage_id))

def load_customer_for_rental(room_name=None, customer_name=None):
    customer = db.session.query(Customer.name, Room.room_name, RentalVoucher.check_in_date, RentalVoucher.check_out_date, RentalVoucher.bill_id) \
        .join(Room, RentalVoucher.room_id.__eq__(Room.id)) \
        .join(Customer, RentalVoucher.customer_id.__eq__(Customer.id))

    if room_name:
        customer = customer.filter(Room.room_name.__eq__(room_name), not Customer.name.__eq__(customer_name))

    return customer.all()

def load_rental_voucher_by(customer_name=None, page=1):
    rental_voucher = db.session.query(Room.room_name, Customer.name,CustomerType.customer_type ,Customer.id_number,
                                      RentalVoucher.check_in_date, RentalVoucher.check_out_date, RentalVoucher.bill_id)\
                     .join(Room, RentalVoucher.room_id.__eq__(Room.id))\
                     .join(Customer, RentalVoucher.customer_id.__eq__(Customer.id)) \
                     .join(CustomerType, Customer.customer_type_id.__eq__(CustomerType.id))

    if customer_name:
        rental_voucher = rental_voucher.filter(Customer.name.contains(customer_name))

    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    end = start + page_size

    return rental_voucher.slice(start, end).all()

def count_rental_vouchers():
    return RentalVoucher.query.count()

def count_order_vouchers():
    return OrderVoucher.query.count()

def load_room_left():
   return db.engine.execute(text("SELECT id FROM room WHERE id not in (SELECT room_id FROM rental_voucher)")).all()


def load_order_voucher():
    return db.session.query(Room.room_name, Customer.name, OrderVoucher.check_in_date, OrderVoucher.check_out_date, OrderVoucher.bill_id)\
                     .join(Room, OrderVoucher.room_id.__eq__(Room.id))\
                     .join(Customer, OrderVoucher.customer_id.__eq__(Customer.id)).all()

def load_order_voucher_by(customer_name=None, page=1):
    order_voucher = db.session.query(Room.room_name, Customer.name,CustomerType.customer_type ,Customer.id_number,
                                     OrderVoucher.order_date, OrderVoucher.check_in_date, OrderVoucher.check_out_date, OrderVoucher.bill_id)\
                     .join(Room, OrderVoucher.room_id.__eq__(Room.id))\
                     .join(Customer, OrderVoucher.customer_id.__eq__(Customer.id)) \
                     .join(CustomerType, Customer.customer_type_id.__eq__(CustomerType.id))

    if customer_name:
        order_voucher = order_voucher.filter(Customer.name.contains(customer_name))

    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    end = start + page_size

    return order_voucher.slice(start, end).all()

def load_room_empty(from_date=None, to_date=None, page=1):
    room = db.session.query(RoomType.room_type_name.distinct(), RoomType.maximum_customer,RoomType.price, Room.description, Room.status,
                            OrderVoucher.check_in_date, OrderVoucher.check_out_date, Room.room_name)\
                            .join(Room, OrderVoucher.room_id.__eq__(Room.id))\
                            .join(RoomType, Room.room_type_id.__eq__(RoomType.id))

    room = room.filter(Room.status.__eq__('NONE'))

    # if from_date and to_date:
    #     if (OrderVoucher.check_out_date.__le__(from_date)):
    #         room = room.filter(OrderVoucher.check_out_date.__le__(from_date))
    #     elif (OrderVoucher.check_in_date.__ge__(to_date)):
    #         room = room.filter(OrderVoucher.check_in_date.__ge__(to_date))

    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    end = start + page_size

    return room.slice(start, end).all()

def count_room_empty():
    room = db.session.query(RoomType.room_type_name, RoomType.maximum_customer, RoomType.price, Room.description,
                            Room.status,
                            OrderVoucher.check_in_date, OrderVoucher.check_out_date) \
                            .join(Room, OrderVoucher.room_id.__eq__(Room.id)) \
                            .join(RoomType, Room.room_type_id.__eq__(RoomType.id))

    room = room.filter(Room.status.__eq__('EMPTY'))

    return room.count()