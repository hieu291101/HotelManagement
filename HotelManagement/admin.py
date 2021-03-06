from datetime import datetime

from HotelManagement import admin, db, utils
from HotelManagement.models import User, Administrator, Customer, CustomerType, Staff, Room, RoomType, Bill, Surchange, \
    RentalVoucher, OrderVoucher
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask_login import logout_user, current_user
from flask import redirect, request


# Đã đăng nhập
class AuthenticationBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.type == 'administrator'

class CommonModelView(ModelView):
    can_view_details = True
    can_export = True
    edit_modal = True
    details_modal = True


    def is_accessible(self):
        return current_user.is_authenticated and current_user.type == 'administrator'


class AdminView(CommonModelView):
    column_exclude_list = ['type']
    column_labels = {
        'username': 'Tài khoản',
        'password': 'Mật khẩu',
        'sex': 'Giới tính',
        'login_status': 'Trạng thái đăng nhập',
        'register_date': 'Ngày đăng ký'
    }
    form_excluded_columns = ['login_status', 'register_date', 'type']


class CustomerView(CommonModelView):
    column_exclude_list = ['type']
    column_labels = {
        'username': 'Tài khoản',
        'password': 'Mật khẩu',
        'sex': 'Giới tính',
        'login_status': 'Trạng thái đăng nhập',
        'register_date': 'Ngày đăng ký',
        'name': 'Họ và tên',
        'id_number': 'Số CMND/CCCD',
        'nationality': 'Quốc tịch',
        'address': 'Địa chỉ',
        'phone_number': 'Số điện thoại',
        'customer_type': 'Loại khách hàng'
    }
    form_excluded_columns = ['rental_vouchers', 'order_vouchers', 'login_status', 'register_date', 'type',
                             'customer_type']


class StaffView(CommonModelView):
    column_exclude_list = ['type']
    column_labels = {
        'username': 'Tài khoản',
        'password': 'Mật khẩu',
        'sex': 'Giới tính',
        'login_status': 'Trạng thái đăng nhập',
        'register_date': 'Ngày đăng ký',
        'name': 'Họ và tên',
        'id_number': 'Số CMND/CCCD',
        'address': 'Địa chỉ',
        'phone_number': 'Số điện thoại',
        'experience': 'Kinh nghiệm'
    }
    form_excluded_columns = ['login_status', 'register_date', 'type']


class CustomerTypeView(CommonModelView):
    column_labels = {
        'customer_type': 'Loại khách hàng',
        'customer_index': 'Hệ số'
    }
    form_excluded_columns = ['customers']


class RoomView(CommonModelView):
    column_exclude_list = ['capacity']
    column_labels = {
        'room_name': 'Tên phòng',
        'status': 'Trạng thái',
        'description': 'Mô tả',
        'room_type': 'Loại phòng',
        'maximum_customer': 'Số người tối đa'
    }
    form_excluded_columns = ['rental_vouchers', 'order_vouchers', 'status', 'capacity']


class RoomTypeView(CommonModelView):
    column_labels = {
        'room_type_name': 'Tên loại phòng',
        'price': 'Giá phòng(nghìn đồng)',
    }
    form_excluded_columns = ['rooms']


class BillView(CommonModelView):
    # can_create = False
    can_edit = False
    column_display_pk = True
    column_labels = {
        'id': 'Mã hóa đơn',
        'unit_price': 'Tổng tiền',
        'surchange': 'Phụ thu'
    }


class SurchangeView(CommonModelView):
    column_display_pk = True
    column_labels = {
        'id': 'Mã phụ thu',
        'surchange': 'Phụ thu'
    }
    form_excluded_columns = ['bills']


class RentalVoucherView(CommonModelView):
    # can_create = False
    # can_edit = False
    column_labels = {
        'check_in_date': 'Ngày nhận phòng',
        'check_out_date': 'Ngày trả phòng',
        'customer': 'Mã khách hàng',
        'room': 'Mã phòng',
        'bill': 'Mã hóa đơn'
    }


class OrderVoucherView(CommonModelView):
    # can_create = False
    can_edit = False
    column_labels = {
        'order_date': 'Ngày đặt phòng',
        'check_in_date': 'Ngày nhận phòng',
        'check_out_date': 'Ngày trả phòng',
        'customer': 'Mã khách hàng',
        'room': 'Mã phòng',
        'bill': 'Mã hóa đơn'
    }


class LogoutView(AuthenticationBaseView):
    @expose('/')
    def index(self):
        logout_user()

        return redirect('/admin')


class StatsView(BaseView):
    @expose('/')
    def index(self):
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        month = request.args.get("year", datetime.now().year)
        mon = request.args.get("year", datetime.now().year)
        kw = request.args.get('kw')
        keyy = request.args.get('keyy')
        year = request.args.get('year')

        return self.render('admin/stats.html',
                           stats=utils.month_stats(mon=2021, from_date=from_date,
                                                   to_date=to_date, keyy=keyy, year=year),
                           count=utils.count_stats(month=2021, kw=kw))


admin.add_view(CommonModelView(User, db.session, name='Người dùng'))
admin.add_view(AdminView(Administrator, db.session, name='admin'))
admin.add_view(CustomerView(Customer, db.session, name='Thông tin khách hàng', category='Khách hàng'))
admin.add_view(CustomerTypeView(CustomerType, db.session, name='Loại khách', category='Khách hàng'))
admin.add_view(StaffView(Staff, db.session, name='Nhân viên'))

admin.add_view(RoomView(Room, db.session, name='Thông tin phòng', category='Phòng'))
admin.add_view(RoomTypeView(RoomType, db.session, name='Loại phòng', category='Phòng'))
admin.add_view(BillView(Bill, db.session, name='Danh sách hóa đơn', category='Hóa đơn'))
admin.add_view(SurchangeView(Surchange, db.session, name='Phụ thu', category='Hóa đơn'))
admin.add_view(RentalVoucherView(RentalVoucher, db.session, name='Phiếu thuê'))
admin.add_view(OrderVoucherView(OrderVoucher, db.session, name='Phiếu đặt'))

admin.add_view(LogoutView(name='Đăng xuất'))
admin.add_view(StatsView(name='Thống kê báo cáo'))

admin.add_sub_category(name="customer", parent_name="Khách hàng")
admin.add_sub_category(name="room", parent_name="Phòng")
admin.add_sub_category(name="bill", parent_name="Hóa đơn")
