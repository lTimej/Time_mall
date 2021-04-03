let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: getCookie('username'),
        orders : JSON.parse(JSON.stringify(orders))
    },
    mounted(){
    },
    methods: {
        // 发起支付
        order_payment(){
            // let order_id = get_query_string('order_id');
            let order_id = this.orders.order_id;
            let url = '/payment/' + order_id + '/';
            axios.get(url, {
                responseType: 'json'
            })
                .then(res => {
                    if (res.data.code == '0') {
                        // 跳转到支付宝
                        location.href = res.data.alipay_url;
                    } else if (res.data.code == '4101') {
                        location.href = '/login/?next=/user/order/1/';
                    } else {
                        console.log(response.data);
                        alert(response.data.errmsg);
                    }
                })
                .catch(error => {
                    console.log(error.response);
                })
        },
    }
});