import hashlib
from sqlalchemy import text, extract, func, join
from HotelManagement import db
from HotelManagement.models import User, RentalVoucher, Room, Surchange, Bill, RoomType


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


def month_stats(from_date=None, to_date=None, kw=None):
    # s = db.session.query(extract('month', RentalVoucher.check_in_date), Room.room_type_id,
    #                      func.sum(Bill.unit_price * Surchange.surchange + Bill.unit_price), func.count(Bill.id)) \
    #      .join(Bill, Bill.surchage_id.__eq__(Surchange.id)) \
    #      .join(RentalVoucher, RentalVoucher.bill_id.__eq__(Bill.id)) \
    #      .join(RentalVoucher, RentalVoucher.room_id.__eq__(Room.id)) \
    # .filter(extract('year', RentalVoucher.check_in_date) == month) \
    #     .group_by(extract('month', RentalVoucher.check_in_date))
    s = db.engine.execute(
        text("SELECT month(v.check_in_date), r.room_type_id, sum(b.unit_price*s.surchange+b.unit_price),count(b.id) "
             "FROM room r, bill b, surchange s, rental_voucher v "
             "WHERE  b.surchage_id=s.id and v.room_id=r.id and v.bill_id=b.id "
             "GROUP BY month(v.check_in_date) "
             "ORDER BY month(v.check_in_date) "))

    return s.all()


def count_stats(year):
    i = db.engine.execute(
        text("SELECT month(v.check_in_date), r.room_name, datediff(v.check_out_date, v.check_in_date) "
             "FROM room r, rental_voucher v "
             "WHERE v.room_id=r.id "
             "GROUP BY month(v.check_in_date) "
             "ORDER BY month(v.check_in_date) "))
    # i = db.session.query(extract('month', RentalVoucher.check_in_date), Room.room_name,
    #                      func.datediff(RentalVoucher.check_out_date, RentalVoucher.check_in_date)) \
    #     .join(RentalVoucher, RentalVoucher.room_id.__eq__(Room.id), isouter=True) \
    #     .filter(extract('year', RentalVoucher.check_in_date) == year) \
    #     .group_by(extract('month', RentalVoucher.check_in_date))

    return i.all()
