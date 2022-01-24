import hashlib
import jwt

from flask import flash, url_for, render_template, session
from flask_mail import Message
from sqlalchemy import text, extract, func, join
from HotelManagement import db, app, mail
from flask_login import current_user
from sqlalchemy import text, extract, func
from HotelManagement.models import User, Customer, RentalVoucher, OrderVoucher, Room, Bill, Surchange, CustomerType, \
    RoomType, Status

def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_customer_by_cmnd(cmnd=None):
    if cmnd:
        cmnd = cmnd.strip()
        return Customer.query.filter(Customer.id_number.__eq__(cmnd))


def check_login(username, password):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        return User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password)).first()


def check_reset_password(username, email):
    if username and email:
        return Customer.query.filter(Customer.username.__eq__(username.strip()),
                                     Customer.email.__eq__(email)).first()


def check_date(orderdate, checkindate):
    if checkindate and orderdate:
        delta = checkindate - orderdate
        if delta.days > 28:
            return False
    return True


# def update_customer(name, username, email, phone, identity, nationality,
#                     gender, address, password, **kwargs):
#     customer = Customer.query.filter(Customer.id_number.__eq__(identity))
#     customer = customer.update({Customer.name: name, Customer.email: email,
#                                 Customer.phone_number: phone, Customer.id_number: identity,
#                                 Customer.nationality: nationality,
#                                 Customer.gender: gender, Customer.address: address})


def add_customer(name, username, email, phone, identity, nationality,
                 gender, address, password, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    name = str(name).strip()
    username = str(username).strip()
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
    return db.session.query(Room.room_name, Customer.name, RentalVoucher.check_in_date, RentalVoucher.check_out_date,
                            RentalVoucher.bill_id) \
        .join(Room, RentalVoucher.room_id.__eq__(Room.id)) \
        .join(Customer, RentalVoucher.customer_id.__eq__(Customer.id)).all()


def load_income():
    income = db.session.query(Room.room_name, Customer.id_number, Customer.name, RentalVoucher.check_in_date,
                              RentalVoucher.check_out_date,
                              Bill.unit_price, Bill.status, Surchange.surchange) \
        .join(Room, RentalVoucher.room_id.__eq__(Room.id)) \
        .join(Customer, RentalVoucher.customer_id.__eq__(Customer.id)) \
        .join(Bill, RentalVoucher.bill_id.__eq__(Bill.id)) \
        .join(Surchange, Surchange.id.__eq__(Bill.surchage_id))


def load_customer_for_rental(room_name=None, customer_name=None):
    customer = db.session.query(Customer.name, Room.room_name, RentalVoucher.check_in_date,
                                RentalVoucher.check_out_date, RentalVoucher.bill_id) \
        .join(Room, RentalVoucher.room_id.__eq__(Room.id)) \
        .join(Customer, RentalVoucher.customer_id.__eq__(Customer.id))

    if room_name:
        customer = customer.filter(Room.room_name.__eq__(room_name), not Customer.name.__eq__(customer_name))

    return customer.all()


def load_rental_voucher_by(customer_name=None, page=1):
    rental_voucher = db.session.query(Room.room_name, Customer.name, CustomerType.customer_type, Customer.id_number,
                                      RentalVoucher.check_in_date, RentalVoucher.check_out_date, RentalVoucher.bill_id,
                                      Bill.status) \
        .join(Room, RentalVoucher.room_id.__eq__(Room.id)) \
        .join(Customer, RentalVoucher.customer_id.__eq__(Customer.id)) \
        .join(CustomerType, Customer.customer_type_id.__eq__(CustomerType.id)) \
        .join(Bill, RentalVoucher.bill_id.__eq__(Bill.id))

    if customer_name:
        rental_voucher = rental_voucher.filter(Customer.name.contains(customer_name))

    rental_voucher = rental_voucher.filter(Bill.status.__eq__(Status.NONE))

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
    return db.session.query(Room.room_name, Customer.name, OrderVoucher.check_in_date, OrderVoucher.check_out_date,
                            OrderVoucher.bill_id) \
        .join(Room, OrderVoucher.room_id.__eq__(Room.id)) \
        .join(Customer, OrderVoucher.customer_id.__eq__(Customer.id)).all()


def load_order_voucher_by(customer_name=None, page=1):
    order_voucher = db.session.query(Room.room_name, Customer.name, CustomerType.customer_type, Customer.id_number,
                                     OrderVoucher.order_date, OrderVoucher.check_in_date, OrderVoucher.check_out_date,
                                     OrderVoucher.bill_id) \
        .join(Room, OrderVoucher.room_id.__eq__(Room.id)) \
        .join(Customer, OrderVoucher.customer_id.__eq__(Customer.id)) \
        .join(CustomerType, Customer.customer_type_id.__eq__(CustomerType.id))

    if customer_name:
        order_voucher = order_voucher.filter(Customer.name.contains(customer_name))

    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    end = start + page_size

    return order_voucher.slice(start, end).all()


def room_type():
    return RoomType.query.all()


def load_room_type(page=1):
    room_type = db.session.query(RoomType.id, RoomType.room_type_name, RoomType.description, RoomType.maximum_customer,
                                 RoomType.price)

    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    end = start + page_size

    return room_type.slice(start, end).all()


def count_room_type():
    return RoomType.query.count()


def count_room_full_by(from_date=None, to_date=None, room_type=None):
    room = db.session.query(RoomType.room_type_name, RoomType.maximum_customer, RoomType.price, Room.status,
                            OrderVoucher.check_in_date, OrderVoucher.check_out_date, Room.room_name) \
        .join(Room, OrderVoucher.room_id.__eq__(Room.id)) \
        .join(RoomType, Room.room_type_id.__eq__(RoomType.id))

    if room_type:
        room = room.filter(RoomType.room_type_name.__eq__(room_type))

    if from_date:
        room = room.filter(OrderVoucher.check_out_date.__ge__(from_date))
    if to_date:
        room = room.filter(OrderVoucher.check_in_date.__le__(to_date))

    return room.count()


def count_room_empty(room_type):
    room = db.session.query(RoomType.room_type_name, RoomType.maximum_customer, RoomType.price, Room.status,
                            Room.room_name) \
        .join(RoomType, Room.room_type_id.__eq__(RoomType.id))

    if room_type:
        room = room.filter(RoomType.room_type_name.__eq__(room_type))

    return room.count()


def count_order(order):
    total_quantity, total_amount = 0, 0

    if order:
        for c in order.values():
            total_quantity += c['quantity']
            total_amount += c['quantity'] * c['price']

    return {
        'total_quantity': total_quantity,
        'total_amount': total_amount
    }


def month_stats(mon, from_date=None, to_date=None, keyy=None, year=None):
    s = db.session.query(extract('month', RentalVoucher.check_in_date), RoomType.room_type_name,
                         func.sum(Bill.unit_price * Surchange.surchange + Bill.unit_price), func.count(Bill.id)) \
        .join(Bill, RentalVoucher.bill_id.__eq__(Bill.id), isouter=True) \
        .join(Room, RentalVoucher.room_id.__eq__(Room.id), isouter=True) \
        .join(RoomType, Room.room_type_id.__eq__(RoomType.id), isouter=True) \
        .join(Surchange, Bill.surchage_id.__eq__(Surchange.id), isouter=True) \
        .filter(extract('year', RentalVoucher.check_in_date) == mon) \
        .group_by(RoomType.room_type_name) \
        .order_by(RoomType.room_type_name)

    if from_date:
        s = s.filter(RentalVoucher.check_in_date.__ge__(from_date))
    if to_date:
        s = s.filter(RentalVoucher.check_in_date.__le__(to_date))
    if keyy:
        s = s.filter(extract('month', RentalVoucher.check_in_date).__eq__(keyy))
    if year:
        s = s.filter(extract('year', RentalVoucher.check_in_date).__eq__(year))

    return s.all()


# def sum_grade(S=0):
#     i = func.sum(Bill.unit_price * Surchange.surchange + Bill.unit_price)
#     n = func.count(RoomType.room_type_name)
#     for i in (1, n+1):
#         S += i
#     return S


def count_stats(month, kw=None):
    i = db.session.query(extract('month', RentalVoucher.check_in_date), Room.room_name,
                         func.sum(func.datediff(RentalVoucher.check_out_date, RentalVoucher.check_in_date))) \
        .join(Room, RentalVoucher.room_id.__eq__(Room.id), isouter=True) \
        .filter(extract('year', RentalVoucher.check_in_date) == month) \
        .group_by(Room.room_name) \
        .order_by(Room.room_name)

    if kw:
        i = i.filter(extract('month', RentalVoucher.check_in_date).__eq__(kw))

    return i.all()



def add_order(name, username, email, phone, identity, nationality,
              gender, address, password, room_name, check_in_date, check_out_date, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    name = str(name).strip()
    username = str(username).strip()
    customer_type_id = '1' if nationality == "Việt Nam" else '2'
    location_id = '1'
    room = load_room_by(room_name=room_name)

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

    bill = Bill(surchage_id=1)
    db.session.add(bill)
    db.session.commit()

    order_voucher = OrderVoucher(room_id=room.id, customer_id=customer.id,
                                 check_in_date=check_in_date,
                                 check_out_date=check_out_date, bill_id=bill.id)


    db.session.add(order_voucher)
    db.session.commit()

def add_order_for_customer(room_type, unit_price):
    bill = Bill(unit_price=unit_price,surchage_id=1)
    db.session.add(bill)
    db.session.commit()

    room = load_room_order_for_customer(room_type=room_type)
    order_voucher = OrderVoucher(room_id=room.id, customer_id=current_user,
                                 check_in_date=session.get('checkindate'),
                                 check_out_date=session.get('checkindate'), bill_id=bill.id)
    db.session.add(order_voucher)
    db.session.commit()

def load_room_order(from_date=None, to_date=None, room_type=None, page=1):
    room = db.session.query(Room.id).select_from(Room) \
        .join(Room.order_vouchers)
    if from_date:
        room = room.filter(OrderVoucher.check_out_date.__ge__(from_date))
    if to_date:
        room = room.filter(OrderVoucher.check_in_date.__le__(to_date))

    room1 = db.session.query(RoomType.room_type_name, RoomType.maximum_customer, RoomType.price, Room.id, Room.status,
                             Room.room_name) \
        .join(RoomType, Room.room_type_id.__eq__(RoomType.id))

    room1 = room1.filter(~Room.id.in_(room))

    if room_type:
        room1 = room1.filter(RoomType.room_type_name.contains(room_type))

    session['counter_room_to_order'] = room1.count()

    page_size = app.config['PAGE_SIZE_ROOM_ORDER']
    start = (page - 1) * page_size
    end = start + page_size

    return room1.slice(start, end).all();

def load_room_order_for_customer(from_date=None, to_date=None, room_type=None):
    room = db.session.query(Room.id).select_from(Room) \
        .join(Room.order_vouchers)
    if from_date:
        room = room.filter(OrderVoucher.check_out_date.__ge__(from_date))
    if to_date:
        room = room.filter(OrderVoucher.check_in_date.__le__(to_date))

    room1 = db.session.query(RoomType.room_type_name, RoomType.maximum_customer, RoomType.price, Room.id, Room.status,
                             Room.room_name) \
        .join(RoomType, Room.room_type_id.__eq__(RoomType.id))

    room1 = room1.filter(~Room.id.in_(room))

    if room_type:
        room1 = room1.filter(RoomType.room_type_name.__eq__(room_type))

    return room1.first()

# def load_room_order_customer(from_date=None, to_date=None, room_type=None):
#     room = db.session.query(Room.id).select_from(Room) \
#         .join(Room.order_vouchers)
#     if from_date:
#         room = room.filter(OrderVoucher.check_out_date.__ge__(from_date))
#     if to_date:
#         room = room.filter(OrderVoucher.check_in_date.__le__(to_date))
#
#     room1 = db.session.query(RoomType.room_type_name, RoomType.maximum_customer, RoomType.price, Room.id, Room.status,
#                              Room.room_name) \
#         .join(RoomType, Room.room_type_id.__eq__(RoomType.id))
#
#     room1 = room1.filter(~Room.id.in_(room))
#
#
#     if room_type:
#         room1 = room1.filter(Customer.name.__eq__(room_type))
#
#     return room1.first()

def load_room_by(room_name=None):
    room = db.session.query(Room.id, Room.status,
                            Room.room_name)

    if room_name:
        room = room.filter(Room.room_name.__eq__(room_name))

    return room.first()

def load_room_by_type(room_type=None):
    room = db.session.query(Room.id, Room.status,
                            Room.room_name)

    if room_type:
        room = room.filter(Room.room_name.__eq__(room_type))

    return room.first()



def load_customer_by(customer_name=None):
    customer = db.session.query(Customer)
    if customer_name:
        customer = customer.filter(Customer.name.__eq__(customer_name))

    return customer.first()


def change_bill_status(bill_id):
    bill = db.session.query(Bill).get(bill_id)
    bill.status = Status.DONE
    db.session.commit()

    return bill


def move_order_to_rental(room_name, customer_name, check_in_date, check_out_date, bill_id):
    room = load_room_by(room_name=room_name)
    customer = load_customer_by(customer_name=customer_name)

    rental_voucher = RentalVoucher(room_id=room.id, customer_id=customer.id,
                                   check_in_date=check_in_date,
                                   check_out_date=check_out_date, bill_id=bill_id)

    rental_voucher1 = db.session.query(RentalVoucher)
    rental_voucher1 = rental_voucher1.filter(RentalVoucher.room_id.__eq__(room.id))
    rental_voucher1 = rental_voucher1.filter(RentalVoucher.customer_id.__eq__(customer.id))
    if rental_voucher1:
        rental_voucher1.delete()

    order_voucher = db.session.query(OrderVoucher)
    order_voucher = order_voucher.filter(OrderVoucher.room_id.__eq__(room.id))
    order_voucher = order_voucher.filter(OrderVoucher.customer_id.__eq__(customer.id))
    if order_voucher:
        order_voucher.delete()

    db.session.add(rental_voucher)

    db.session.commit()

    return rental_voucher
# def load_room_not_in(room_id=None):

# def add_order_voucher()


##########################
##########################
def send_email(customer):
    token = Customer.get_reset_token(customer)
    msg = Message()
    msg.subject = "Hotel App Password Reset"
    msg.sender = "thanhdinhc2810@gmail.com"
    msg.recipients = [customer.email]
    msg.body = 'testing'

    msg.html = render_template('reset_email.html',
                               customer=customer,
                               token=token)
    mail.send(msg)


def verify_reset_token(token):
    try:
        username = jwt.decode(token, key=app.secret_key,
                              algorithms=['HS256'])['reset_password']
        print(username)
    except Exception as e:
        print(e)
        return
    return User.query.filter_by(username=username).first()

