from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, backref
from HotelManagement import db
from datetime import datetime
from flask_login import UserMixin
from enum import Enum as UserEnum


class UserRole(UserEnum):
    ADMIN = 1
    STAFF = 2
    CUSTOMER = 3


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    login_status = Column(Boolean, default=True)
    register_date = Column(DateTime, default=datetime.now())

    avatar = Column(String(100))
    # type = Column(String(20))
    user_role = Column(Enum(UserRole), default=UserRole.CUSTOMER)

    # __mapper_args__ = {
    #     'polymorphic_on': type
    # }


class Customer(User):
    __tablename__ = 'customer'

    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    name = Column(String(30), nullable=False)
    gender = Column(String(5), nullable=False)
    email = Column(String(10), nullable=False)
    id_number = Column(String(10), nullable=False)  # Căn cước công dân
    nationality = Column(String(20), nullable=False)
    address = Column(String(60), nullable=False)
    phone_number = Column(String(10), nullable=False)

    location_id = Column(Integer, ForeignKey('location.id'), nullable=False)
    customer_type_id = Column(Integer, ForeignKey('customer_type.id'), nullable=False)
    rental_vouchers = relationship('RentalVoucher', backref='customer', lazy=True)
    order_vouchers = relationship('OrderVoucher', backref='customer', lazy=True)

    __mapper_args__ = {
        'polymorphic_identity': 'customer'
    }

    def __str__(self):
        return self.id


class CustomerType(db.Model):
    __tablename__ = 'customer_type'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_type = Column(String(20), default='Nội địa')
    customer_index = Column(Integer, nullable=False, default=1)
    customers = relationship("Customer", backref='customer_type', lazy=True)

    def __str__(self):
        return self.customer_type


class Staff(User):
    __tablename__ = 'staff'

    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    name = Column(String(30), nullable=False)
    gender = Column(String(5), nullable=False)
    email = Column(String(10), nullable=False)
    id_number = Column(String(10), nullable=False)
    address = Column(String(60), nullable=False)
    location_id = Column(Integer, ForeignKey('location.id'), nullable=False)
    phone_number = Column(String(10), nullable=False)
    experience = Column(Integer, nullable=False)  # số tháng làm việc

    __mapper_args__ = {
        'polymorphic_identity': 'staff'
    }


class Location(db.Model):
    __tablename__ = 'location'

    id = Column(Integer, primary_key=True)
    city = Column(String(20), nullable=False)
    country = Column(String(20), nullable=False)

    staff = relationship("Staff", backref='location', lazy=True)
    customer = relationship("Customer", backref='location', lazy=True)


class Administrator(User):
    __tablename__ = 'admin'

    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    email = Column(String(50), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'administrator'
    }


class Room(db.Model):
    __tablename__ = 'room'

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_name = Column(String(10), nullable=False)
    status = Column(Boolean, default=True)
    capacity = Column(Integer, nullable=False, default=0)  # số người trên phòng
    description = Column(String(60))

    room_type_id = Column(Integer, ForeignKey('room_type.id'), nullable=False)
    rental_vouchers = relationship('RentalVoucher', backref='room', lazy=True)
    order_vouchers = relationship('OrderVoucher', backref='room', lazy=True)

    def __str__(self):
        return self.id


class RoomType(db.Model):
    __tablename__ = 'room_type'

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_type_name = Column(String(20), nullable=False)
    maximum_customer = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)

    rooms = relationship('Room', backref='room_type', lazy=False)

    def __str__(self):
        return self.room_type_name


class Bill(db.Model):
    __tablename__ = 'bill'

    id = Column(Integer, primary_key=True, autoincrement=True)
    unit_price = Column(Float, default=0)

    surchage_id = Column(Integer, ForeignKey('surchange.id'), nullable=False)
    rental_voucher = relationship('RentalVoucher', backref=backref('bill', uselist=False, lazy=True),
                                  foreign_keys='[RentalVoucher.bill_id]', uselist=False, lazy=True)
    order_voucher = relationship('OrderVoucher', backref=backref('bill', uselist=False, lazy=True),
                                 foreign_keys='[OrderVoucher.bill_id]', uselist=False, lazy=True)

    def __str__(self):
        return self.id


class Surchange(db.Model):
    __tablename__ = 'surchange'

    id = Column(Integer, primary_key=True, autoincrement=True)
    surchange = Column(Float, default=0.25, unique=True)

    bills = relationship('Bill', backref='surchange', lazy=True)

    def __str__(self):
        return str(self.surchange)


class RentalVoucher(db.Model):
    __tablename__ = 'rental_voucher'

    room_id = Column(Integer, ForeignKey('room.id'), primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer.id'), primary_key=True)
    check_in_date = Column(DateTime, default=datetime.now())
    check_out_date = Column(DateTime, default=datetime.now())

    bill_id = Column(Integer, ForeignKey('bill.id'), nullable=False)


class OrderVoucher(db.Model):
    __tablename__ = 'order_voucher'

    room_id = Column(Integer, ForeignKey('room.id'), primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer.id'), primary_key=True)
    order_date = Column(DateTime, default=datetime.now())
    check_in_date = Column(DateTime, default=datetime.now())
    check_out_date = Column(DateTime, default=datetime.now())

    bill_id = Column(Integer, ForeignKey('bill.id'), nullable=False)

    def __str__(self):
        return self.name


if __name__ == "__main__":
    db.create_all()
