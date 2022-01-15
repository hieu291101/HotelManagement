function addToOrder(check_in_date, check_out_date, people){
    alert("Hello")

    fetch('/api/add-order', {
        method: 'post',
        body: JSON.stringify({
            'check_in_date': check_in_date
            'check_out_date': check_out_date
            'people': people
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
}