function addToOrder(id, room_type_name, capacity, price){

    fetch('/api/add-order', {
        method: 'post',
        body: JSON.stringify({
            'id': id,
            'room_type_name': room_type_name,
            'capacity': capacity,
            'price': price
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function(res){
        console.info(res)
        return res.json()
    }).then(function(data){
        console.info(data)
        let counter = document.getElementById('orderCounter')
        counter.innerText = data.total_quantity
    }).catch(function(err){
        console.error(err)
    })
}

function addOrderVoucher(roomName) {
    let choice = confirm('Bạn có chắc chắn đặt phòng hay không?')
    let name = document.getElementsByName('name')
    let email = document.getElementsByName('email')
    let phone = document.getElementsByName('phone')
    let identity = document.getElementsByName('identity')
    let nationality = document.getElementsByName('nationality')
    let gender = document.getElementsByName('gender')
    let address = document.getElementsByName('address')
    let check_in_date = document.getElementsByName('checkindate')
    let check_out_date = document.getElementsByName('checkoutdate')
    fetch('/api/order-voucher', {
        method: 'post',
        body: JSON.stringify({
            'room_name': roomName,
            'name': name[0].value,
            'email': email[0].value,
            'phone': phone[0].value,
            'identity': identity[0].value,
            'nationality': nationality[0].value,
            'gender': gender[0].value,
            'address': address[0].value,
            'check_in_date': check_in_date[0].value,
            'check_out_date': check_out_date[0].value
        }),
        headers: {
            'Content-Type':' application/json'
        }
    }).then(res => res.json()).then(data => {
        if (data.status == 201) {
            alert('Đặt thành công')
            location.reload()
        } else if (data.status == 404)
            alert(data.err_msg)
    })
}

function addOrderVoucherForCustomer() {
    roomType = document.getElementsByName('roomtype')
    quantity = document.getElementsByName('quantity')
    unitPrice = document.getElementsByName('unitprice')

    let choice = confirm('Bạn có chắc chắn đặt phòng hay không?')
    fetch('/api/order-voucher-customer', {
        method: 'post',
        body: JSON.stringify({
            'room_type': roomType,
            'unit_price': unitPrice,
            'quantity': quantity
        }),
        headers: {
            'Content-Type':' application/json'
        }
    }).then(res => res.json()).then(data => {
        if (data.status == 201) {
            alert('Đặt thành công')
            location.reload()
        } else if (data.status == 404)
            alert(data.err_msg)
    })
}

function updateStatusBill(billId) {
    let choice = confirm('Bạn có chắc chắn thanh toán hay không?')
    if(choice == true) {
        fetch('/api/payment', {
        method: 'post',
        body: JSON.stringify({
            'bill_id': billId
        }),
        headers: {
            'Content-Type':' application/json'
        }
    }).then(res => res.json()).then(data => {
        if (data.status == 201) {
            confirm('Thanh toán thành công')
            location.reload()
        } else if (data.status == 404)
            alert(data.err_msg)
    })
    }
}

function moveOrderToRental(roomName, customerName, checkInDate, checkOutDate, billId) {
    let choice = confirm('Bạn có chắc chắn thuê hay không?')
    if (choice == true) {
        fetch('/api/order-to-rental', {
        method: 'post',
        body: JSON.stringify({
            'room_name': roomName,
            'customer_name': customerName,
            'check_in_date': checkInDate,
            'check_out_date': checkOutDate,
            'bill_id': billId
        }),
        headers: {
            'Content-Type':' application/json'
        }
        }).then(res => res.json()).then(data => {
            if (data.status == 201) {
                alert('Thuê thành công')
                location.reload()
            } else if (data.status == 404)
                alert(data.err_msg)
        })
    }

}