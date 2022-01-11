import hashlib
from sqlalchemy import text
from HotelManagement import db
from HotelManagement.models import User


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


def month_stats():
    # return db.session.query(Room.room_type_id, extract('month', RentalVoucher.check_in_date),
    #                         func.sum(Bill.unit_price * Surchange.surchange + Bill.unit_price), func.count(Bill.id)) \
    #     .join(RentalVoucher, RentalVoucher.bill_id.__eq__(Bill.id)) \
    #     .join(Bill, Bill.surchage_id.__eq__(Surchange.id)) \
    #     .join(RentalVoucher, RentalVoucher.room_id.__eq__(Room.id)) \
    #     .filter(extract('year', RentalVoucher.check_in_date) == year) \
    #     .group_by(extract('month', RentalVoucher.check_in_date)).all()
    s = db.engine.execute(text("SELECT r.room_type_id, sum(b.unit_price*s.surchange+b.unit_price), count(b.id), "
                               "month(v.check_in_date) "
                               "FROM room r, bill b, surchange s, rental_voucher v "
                               "WHERE  b.surchage_id=s.id and v.room_id=r.id and v.bill_id=b.id "
                               "GROUP BY month(v.check_in_date) "
                               "ORDER BY month(v.check_in_date) "))
    return s


def count_stats():
    return db.engine.execute(
        text("SELECT month(v.check_in_date), r.room_name, datediff(v.check_out_date, v.check_in_date) "
             "FROM room r, rental_voucher v "
             "WHERE v.room_id=r.id "
             "ORDER BY month(v.check_in_date)"))
