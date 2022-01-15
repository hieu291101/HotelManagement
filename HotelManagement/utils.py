import hashlib
from sqlalchemy import text, extract, func, join
from HotelManagement import db
from HotelManagement.models import User, RentalVoucher, Room, Surchange, Bill, RoomType
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
