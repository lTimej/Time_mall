let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: getCookie('username'),
        carts: carts,
        goods_num:1,
        sku_price:0,
        total_count: 0,
        total_selected_count: 0,
        total_selected_amount: 0,
        carts_tmp: [],
        cartLen:cartLen,
        allSelected:true
    },
    computed: {
        // selected_all(){
        //     let selected=true;
        //     for(let i=0; i<this.carts.length; i++){
        //         if(this.carts[i].selected==false){
        //             selected=false;
        //             break;
        //         }
        //     }
        //     return selected;
        // },

    },
    mounted(){
        // // 初始化购物车数据并渲染界面
        this.update_seleted();
        // this.changeAllSel();
        this.eachSelected();
        this.computeSelected();
        //购物车付款导向栏悬浮效果
        xuanfu(this.carts.length);
        // // 计算商品总数量：无论是否勾选
        // this.compute_total_count();
        // // 计算被勾选的商品总金额和总数量
        // this.compute_total_selected_amount_count();
        if (this.carts.length === 0)
        this.allSelected = false
    },
    methods: {
        // 修改selected
        update_seleted(){
            // 渲染界面
            this.carts = JSON.parse(JSON.stringify(carts));
            for(let i=0; i<this.carts.length; i++){
                if(this.carts[i].selected=='True'){
                    this.carts[i].selected=true;
                } else {
                    this.carts[i].selected=false;
                }
            }
            // 手动记录购物车的初始值，用于更新购物车失败时还原商品数量
            this.carts_tmp = JSON.parse(JSON.stringify(carts));
        },
        //改变勾选状态
        changeSelected(index){
            let url = "/cartlist/"
            axios.put(url,{
                sku_id:this.carts[index].sku_id,
                count:this.carts[index].count,
                selected:this.carts[index].selected,
                price:this.carts[index].now_price,
            },{
                headers:{
                    'X-CSRFToken':getCookie('csrftoken')
                },responseType:'json'
            }).then(res=>{
                if (res.data.code == '0')
                {
                    this.eachSelected();
                    this.computeSelected()
                }
            }).catch(err=>{

            })
        },
        //点击全选
        Aselected() {
            if (this.allSelected)
            {
                this.carts.forEach(res=>{
                    res.selected = false
                })
            }else
            {
                this.carts.forEach(res=>{
                    res.selected = true
                })
            }
            let url = "/cartlist/selected/"
            axios.put(url,{
                selected:!this.allSelected
            },{
                headers:{
                    'X-CSRFToken':getCookie('csrftoken')
                },
                responseType:'json'
            }).then(res=>{
                console.log(res);
                this.computeSelected()
            }).catch(err=>{
                console.log(err);
            })
        },
        //计算选择的商品
        computeSelected() {
            let num = 0;
            let allPrice = 0;
            this.carts.forEach(res=>{
                if (res.selected)
                {
                    num += parseInt(res.count)
                    allPrice += parseInt(res.count) * parseFloat(res.now_price)
                }
            })
            this.total_selected_count = num;
            this.total_selected_amount = allPrice.toFixed(2)
        },
        //有一个没选，全选不选，全部选中，全选选中
        eachSelected() {
            let obj = this.carts.every(res=>{
                return res.selected == true
            });
            if(obj)
            {
                this.allSelected = true
            }else {
                this.allSelected = false
            }

        },
        //增加商品数量
        addNum(index) {
            let c = 1
            if (this.carts[index].count < 5)
            {
                this.carts[index].count += 1
                c = this.carts[index].count
            }else
            {
                this.carts[index].count = 5
                c = this.carts[index].count
                alert("不能超过5件")
            }
            this.changeCount(index,c)
        },
        //减少商品数量
        subNum(index) {
            let c = 1
            if (this.carts[index].count >1)
            {
                this.carts[index].count -= 1
                c = this.carts[index].count
            }else
            {
                this.carts[index].count = 1
                let d = document.getElementById('subNum')
                if (d.className.indexOf('disable') === -1) {
                    d.className += ' disable'
                }
                c = this.carts[index].count
            }
            this.changeCount(index,c)
        },
        //输入框修改数量
        cNum(index) {
            let c = 1
            if (this.carts[index].count>5)
            {
                c = 5;
                this.carts[index].count = c
                alert("不能超过5件")
            }else
            {
                c = this.carts[index].count
            }
            this.changeCount(index,c)
        },
        //修改商品数量逻辑
        changeCount(index,count){
            let url = "/cartlist/"
            axios.put(url,{
                sku_id:this.carts[index].sku_id,
                count:count,
                selected:this.carts[index].selected,
                price:this.carts[index].now_price,
            },{
                headers:{
                    'X-CSRFToken':getCookie('csrftoken')
                },responseType:'json'
            }).then(res=>{
                if (res.data.code == '0')
                {
                    console.log(res);
                    this.carts[index].sku_amount_price = res.data.cart_sku.sku_amount_price
                    this.computeSelected()
                }
            }).catch(err=>{
                console.log(err);
            })
        },
        // 删除购物车数据
        del_cart(index){
            let url = '/cartlist/';
            axios.delete(url, {
                data: {
                    sku_id: this.carts[index].sku_id
                },
                headers:{
                    'X-CSRFToken':getCookie('csrftoken')
                },
                responseType: 'json',
            }).then(res => {
                    if (res.data.code == '0') {
                        //截去该索引信息
                        this.carts.splice(index, 1);
                        xuanfu(this.carts.length)
                        // 重新计算界面的价格和数量
                        this.computeSelected()
                        //购物车为空，取消全选
                        if (this.carts.length === 0) {this.allSelected = false}
                    } else {
                        alert(response.data.errmsg);
                    }
                })
                .catch(error => {
                    console.log(error);
                })
        },
        //删除多个商品
        del_selected_cart(){
            this.carts.filter(res=>{
                return res.selected===true
            }).forEach((res,index)=>{
                let url = '/cartlist/';
                axios.delete(url, {
                    data: {
                        sku_id: res.sku_id
                    },
                    headers:{
                        'X-CSRFToken':getCookie('csrftoken')
                    },
                    responseType: 'json',
                }).then(res => {
                        if (res.data.code == '0') {
                            //截去该索引信息
                            this.carts.splice(index, 1);
                            xuanfu(this.carts.length)
                            // 重新计算界面的价格和数量
                            this.computeSelected()
                            //购物车为空，取消全选
                            if (this.carts.length === 0) {this.allSelected = false}
                        } else {
                            alert(response.data.errmsg);
                        }
                    })
                .catch(error => {
                    console.log(error);
                })
            })
        },
        //清空
        clear_cart(){
            this.carts.forEach((res,index)=>{
                let url = '/cartlist/';
                axios.delete(url, {
                    data: {
                        sku_id: res.sku_id
                    },
                    headers:{
                        'X-CSRFToken':getCookie('csrftoken')
                    },
                    responseType: 'json',
                }).then(res => {
                        if (res.data.code == '0') {
                            //截去该索引信息
                            this.carts.splice(index, 1);
                            xuanfu(this.carts.length)
                            // 重新计算界面的价格和数量
                            this.computeSelected()
                            //购物车为空，取消全选
                            if (this.carts.length === 0) {this.allSelected = false}
                        } else {
                            alert(response.data.errmsg);
                        }
                    })
                .catch(error => {
                    console.log(error);
                })
            })
        }
    }
});