let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: getCookie('username'),
        carts:carts,
        addresses:JSON.parse(JSON.stringify(addresses)),
        default_address_id:default_address_id,
        cartLen:0,
        order_submitting: false,
        isShowAddr:false,
        province:[],
        city:[],
        countryside:[],
        province_dict:{
            province_id:'',
            city_id:'',
            district_id:'',
            email:'',
            place:"",
            receiver:"",
            mobile:"",
        },
        newCreate_edit_index:'',
        addrSelec:0,
        currAddr:{},
        code:code,

        error_receiver:false,
        error_place:false,
        error_mobile:false,
        error_email:false,
        error_all:false,
        pay_method: 2,
        // nowsite: '',
        // payment_amount: '',
    },
    mounted(){
        //moqui省份信息
        this.get_province();
        this.showAddr();
        this.changeAddr(this.addrSelec)
        // 初始化支付金额
        // this.payment_amount = payment_amount;
        // // 绑定默认地址
        // this.nowsite = default_address_id;
        this.isOrder();


    },
    computed:{
        //商品总数
        total_goods(){
            return this.carts.length;
        },
        //商品总价格（未打则）
        total_price(){
            let p = this.carts.reduce((pre,curr)=>{
                pre = pre + parseFloat(curr.sku_amount_price)
                return pre
            },parseFloat(0))
            t = p.toFixed(2)
            return t
        },
        //打折后总价格
        origin_price(){
            let p = this.carts.reduce((pre,curr)=>{
                pre = pre + parseInt(curr.count)*parseFloat(curr.price)
                return pre
            },parseFloat(0))
            t = p.toFixed(2)
            return t
        },
        //优惠总价格
        yh(){
            return (this.total_price - this.origin_price).toFixed(2)
        }
    },
    methods:{
        //判断订单是否存在
        isOrder(){
            if (this.code === '0'){
                alert("订单失效")
                location.href = '/user/order/1'
            }
        },
        //使用新地址
        useNewAddr() {
            this.newCreate_edit_index = -1
            this.into_clear_table()
        },
        //编辑地址
        address_edit(index){
            this.newCreate_edit_index = index
            this.into_clear_table(index)
        },
        //点击编辑将信息填入表中
        into_clear_table(index=-1){
            if (index === -1){
                this.province_dict.receiver = ''
                this.province_dict.province_id = ''
                this.province_dict.city_id = ''
                this.province_dict.district_id = ''
                this.province_dict.place = ''
                this.province_dict.mobile = ''
                this.province_dict.email = ''
                this.isShowAddr = true
            }else{
                this.province_dict.receiver = this.addresses[index].receiver
                this.province_dict.province_id = this.addresses[index].province_id
                this.province_dict.city_id = this.addresses[index].city_id
                this.province_dict.district_id = this.addresses[index].district_id
                this.province_dict.place = this.addresses[index].place
                this.province_dict.mobile = this.addresses[index].mobile
                this.province_dict.email = this.addresses[index].email
                this.isShowAddr = true
            }
        },
        //取消修改地址
        cancel_addr_upd() {
            this.isShowAddr = false;
        },
        //切换收获地址
        changeAddr(index){
            this.addrSelec = index
            this.currAddr = this.addresses[index]
        },
        //获取省份信息
        get_province() {
            let url = "/areas/"
            axios.get(url,{
                responseType:'json'
            }).then(res=>{
                this.province = res.data.province_list
            }).catch(err=>{
                console.log(err);
            })
        },
        //校验
        checkReceiver(){
            if (!this.province_dict.receiver)
            {
                this.error_receiver = true;
            }else{
                this.error_receiver = false;
            }
        },
        checkPlace(){
            if (!this.province_dict.place)
            {
                this.error_place = true;
            }else{
                this.error_place = false;
            }
        },
        checkPhone(){
            let re = /^1[3-9]\d{9}$/;
            if (re.test(this.province_dict.mobile)){
                this.error_mobile = false
            }else{
                this.error_mobile = true
            }
        },
        //校验邮箱
        checkEmail() {
            if (!this.province_dict.email)
            {
                this.error_email =false
                return;
            }
            let re = /^[0-9a-zA-Z]{1,16}@(qq||yeah||126||163)\.(net||cn||com)$/
            if (!re.test(this.province_dict.email))
            {
                this.error_email =true
            }else{
                this.error_email =false
            }
        },
        //确认地址
        confirm_btn(){
            this.checkPhone();
            this.checkPlace();
            this.checkReceiver();
            this.checkEmail();
            if (this.error_mobile === true || this.error_place === true || this.error_place === true){
                // 禁用掉表单的提交事件
                window.event.returnValue = false;
            }else{
               if (this.newCreate_edit_index === -1){
                        //增加地址
                    let url = '/address/add/'
                    axios.post(url,this.province_dict,
                    {
                        headers: {'X-CSRFToken':getCookie('csrftoken')},
                        responseType:'json'
                    }).then(res=>{
                        if (res.data.code=='0')
                        {
                            this.addresses.splice(0, 0, res.data.address_dict);
                            this.changeAddr(0);
                            this.showAddr()
                            this.isShowAddr = false;
                        }else if(res.data.code == '5000'){//未登录返回登录页面
                            location.href = '/login/?next=/address/';
                        }else{//地址总数超过20,报错
                            alert(res.data.errmsg)
                        }
                    }).catch(err=>{
                        console.log(err);
                    })
               }else{//编辑
                   let url = '/address/update/' + this.addresses[this.newCreate_edit_index].id +'/'
                    axios.put(url,this.province_dict,
                        {
                            headers: {'X-CSRFToken':getCookie('csrftoken')},
                            responseType:'json'
                    }).then(res=>{
                        if (res.data.code=='0')
                        {
                            this.addresses[this.newCreate_edit_index] = res.data.address_dict;
                            this.changeAddr(this.newCreate_edit_index);
                            this.showAddr()
                            this.isShowAddr = false;
                        }else{//未登录返回登录页面
                            location.href = '/login/?next=/address/';
                        }
                    }).catch(err=>{
                        console.log(err);
                    })
               }
            }

        },

        showAddr(){//只显示4条数据
            this.addresses = this.addresses.splice(0, 4);
        },
        // 提交订单
        submit_order(){
            if (!this.currAddr) {
                alert('请补充收货地址');
                return;
            }
            if (!this.pay_method) {
                alert('请选择付款方式');
                return;
            }
            if (this.order_submitting == false){
                this.order_submitting = true;
                let url = '/order/';
                axios.post(url, {
                    address_id: this.currAddr.id,
                    pay_method: parseInt(this.pay_method),
                    sku_id:this.carts[0].sku_id,
                    count:this.carts[0].count,
                    specs:this.carts[0].sku_specs,
                    id:this.carts[0].id
                }, {
                    headers:{
                        'X-CSRFToken':getCookie('csrftoken')
                    },
                    responseType: 'json'
                })
                    .then(res => {
                        this.order_submitting = false;
                        if (res.data.code == '0') {
                            //作出判断，商品是否存在，库存是否够等
                            alert(res.data.errmsg);
                            location.href = '/order/commit/?order_id='+res.data.order_id
                                        +'&payment_amount='+this.total_price
                                        +'&pay_method='+this.pay_method + "&mv=" + res.data.sku_id + '_' + res.data.sku_count;
                        } else if (res.data.code == '4101') {
                            location.href = '/login/?next=/orderlist/';
                        } else {
                            alert(res.data.errmsg);
                        }
                    })
                    .catch(error => {
                        this.order_submitting = false;
                        console.log(error.response);
                    })
            }
        }

    },
    watch:{//监听省份id，一旦选中某个省份，就立即执行，获取市级
        "province_dict.province_id" :function () {
            if (this.province_dict.province_id)
            {
                let url = '/areas/?areas_id=' + this.province_dict.province_id
                axios.get(url,{
                    responseType: 'json'
                }).then(res=>{
                    if (res.data.code=='0')
                    {
                        this.city = res.data.sub_city_list
                    }else{
                        this.city = []
                    }
                })
            }else{
                this.city = []
            }
        },//监听市id，一旦选中某个市，就立即执行，获取县级
        "province_dict.city_id" :function () {
            if (this.province_dict.city_id)
            {
                let url = '/areas/?areas_id=' + this.province_dict.city_id
                axios.get(url,{
                    responseType: 'json'
                }).then(res=>{
                    if (res.data.code=='0')
                    {
                        this.countryside= res.data.sub_city_list
                    }else{
                        this.countryside= []
                    }
                })
            }else{
                this.countryside= []
            }
        }
    }
});