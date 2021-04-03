let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: getCookie('username'),
        category_id: category_id,
        page_num:page_num,
        total_page:total_page,
        p_r:p_r,
        hots: [],
        cart_total_count: 0,
        carts: [],
        cartss:[],
        goods:JSON.parse(JSON.stringify(goods)),
        spus_dict:JSON.parse(JSON.stringify(spus_dict)),
        breadcrums:JSON.parse(JSON.stringify(breadcrums)),
        sort:sort,
        isShowMenu:false,
        rp:"",
        lp:"",
        cartLen:0
    },
    mounted(){
        // 获取热销商品数据
        this.get_hot_skus();
        // 获取简单购物车数据
        this.getShotCutCarts()
    },
    methods: {
        //价格区间
        submitPrice(){
            this.p_r = this.lp + "_" + this.rp
            location.href = '/goodslist/' + this.category_id + "?p_r=" + this.p_r
        },
        showZhongHe()
        {
            location.href = '/goodslist/' + this.category_id + "?page=1&sort=default" + "&p_r=" + this.p_r
        },
        showPrice()
        {
            location.href = '/goodslist/' + this.category_id + "?page=1&sort=price" + "&p_r=" + this.p_r
        },
        showSales()
        {
            location.href = '/goodslist/' + this.category_id + "?page=1&sort=sales" + "&p_r=" + this.p_r
        },
    	// 获取热销商品数据
        get_hot_skus(){
            if (this.category_id) {
                let url = '/hot/'+ this.category_id +'/';
                axios.get(url, {
                    responseType: 'json'
                })
                    .then(res => {
                        this.hots = res.data.hots;
                        for(let i=0; i<this.hots.length; i++){
                            this.hots[i].url = '/detail/' + this.hots[i].spu_id + '/';
                        }
                    })
                    .catch(error => {
                        console.log(error.res);
                    })
            }
        },
        // 获取简单购物车数据
        getShotCutCarts()
        {
            let url = "/carts/";
            axios.get(url,{
                responseType:'json'
            }).then(res=>{
                this.cartss = res.data.carts
                this.cartLen = res.data.cartLen
            }).catch(err=>{
                console.log(err);
            })
        }
    }
});