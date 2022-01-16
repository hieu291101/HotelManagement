function addToOrder(id, room_type_name, capacity, price){
    let room-left = document.getElementById('room-left')
    if(data.quantity >= room-left) {
        alert("Đã chọn tối đa loại phòng");
        return;
    }

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