import hashlib
from sqlalchemy import text, extract, func, join
from HotelManagement import db
from HotelManagement.models import User, RentalVoucher, Room, Surchange, Bill, RoomType
from HotelManagement.models import User, Customer
from HotelManagement import db

from sqlalchemy import text, extract, func

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

def load_room_type(page=1):
    room_type=db.session.query(RoomType.id, RoomType.room_type_name,RoomType.description,RoomType.maximum_customer, RoomType.price)

    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    end = start + page_size

    return room_type.slice(start, end).all()

def count_room_type():
    return RoomType.query.count()

def count_room_full_by(from_date=None, to_date=None, room_type=None):
    room = db.session.query(RoomType.room_type_name, RoomType.maximum_customer,RoomType.price, Room.status,
                            OrderVoucher.check_in_date, OrderVoucher.check_out_date, Room.room_name)\
                            .join(Room, OrderVoucher.room_id.__eq__(Room.id))\
                            .join(RoomType, Room.room_type_id.__eq__(RoomType.id))

    if room_type:
        room=room.filter(RoomType.room_type_name.__eq__(room_type))

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
        room=room.filter(RoomType.room_type_name.__eq__(room_type))

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

# def add_order(order):
#     if order:
#         order_voucher = OrderVoucher()

# def add_order_voucher()

