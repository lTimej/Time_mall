let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: getCookie('username'),
		sku_id: -1,
        goods_detail:JSON.parse(JSON.stringify(goods_detail)),
        price:goods_detail.price,
        comments:0,
        sales:0,
        now_price:goods_detail.now_price,
        sku_count: 1,
        default_image:goods_detail.default_image,
        color_num:-1,
        size_num:-1,
        isShowXiaotu:-1,
        isShowColor:goods_detail.goods_specs.color,
        isShowSize:goods_detail.goods_specs.size,
        showPanel1:false,
        showPanel2:true,
        spec_ensure:false,
        isBuy:true,
        specs:{},
        cartLen:0,
        cartss: [],
    },
    mounted(){

        // // 获取热销商品数据
        // this.get_hot_skus();
        // // 记录分类商品的访问量
		// this.goods_visit_count();
        // // 保存用户浏览记录
		// this.save_browse_histories();
		// // 获取简单购物车数据
        this.getShotCutCarts()
        // // 获取商品评价信息
        // this.get_goods_comment();
    },
    watch: {
        // // 监听商品数量的变化
        // sku_count: {
        //     handler(newValue){
        //         this.sku_amount = (newValue * this.sku_price).toFixed(2);
        //     },
        //     immediate: true
        // }
        // color_num: {
        //     handler(newValue){
        //         // console.log(newValue);
        //     },
        //     immediate: true
        // }
    },
    methods: {
        // 获取简单购物车数据
        getShotCutCarts() {
            let url = "/carts/";
            axios.get(url,{
                responseType:'json'
            }).then(res=>{
                this.cartss = res.data.carts
                this.cartLen = res.data.cartLen
            }).catch(err=>{
                console.log(err);
            })
        },

        //改变sku默认图片
        changeSku(spec_title,label,spec_id,indey,flag=-1) {
           this.specs[label] = spec_title
            //弹窗逻辑
            if (flag==0)
            {
                if (this.color_num!=indey)
                {
                    this.color_num = indey
                }else
                {
                    this.color_num = -1
                }
            }
            if(flag==1){
                if (this.size_num!=indey)
                {
                    this.size_num = indey
                }else
                {
                    this.size_num = -1
                }
            }
            if (this.isShowSize)
            {
                if (this.size_num!=-1 && this.color_num!=-1)
                {
                    this.spec_ensure = true
                }
                else{
                    this.spec_ensure = false
                }

            }else
            {
                if (this.color_num!=-1)
                {
                    this.spec_ensure = true
                }else{
                    this.spec_ensure = false
                }
            }
            let url = '/sku/'
            axios.get(url,{
                params:{
                    spec_title:spec_title,
                    spec_id:spec_id,
                    label:label,
                    flag:flag
                }
            }).then(res=>{
                this.default_image = res.data.img
                this.comments = res.data.comments
                this.sales = res.data.sales
                this.price = res.data.price
                this.now_price = res.data.now_price
                if (res.data.sku_id)
                {this.sku_id = res.data.sku_id}
            }).catch(err=>{
                console.log(err);
            })
        },
        ShowXiaotu(index,image) {
            this.isShowXiaotu = index
            this.default_image = image
        },
        // // // 加数量
        on_addition(){
            if (this.sku_count < 5) {
                this.sku_count++;
            } else {
                this.sku_count = 5;
                alert('超过商品数量上限');
            }
        },
        // // 减数量
        on_minus(){
            if (this.sku_count > 1) {
                this.sku_count--;
            }
        },
        // // 编辑商品数量
        check_sku_count(){
            if (this.sku_count > 5) {
                this.sku_count = 5;
            }
            if (this.sku_count < 1) {
                this.sku_count = 1;
            }
        },
         // // 加入购物车
        add_carts(){
            this.isBuy = false
            this.showPanel1 = false
            this.showPanel2 = true
            if (this.isShowSize)
            {
                if (this.color_num == -1 || this.size_num == -1 || this.sku_id == -1)
                {
                    this.showPanel1 = true
                    this.showPanel2 = false
                    return
                }
            }else
            {
                if (this.color_num == -1 || this.sku_id == -1)
                {
                    this.showPanel1 = true
                    this.showPanel2 = false
                    return
                }
            }
            let url = '/cartlist/';
            axios.post(url, {
                sku_id: parseInt(this.sku_id),
                count: this.sku_count,
                specs:this.specs,
            }, {
                headers: {
                    'X-CSRFToken':getCookie('csrftoken')
                },
                responseType: 'json',
                withCredentials: true
            })
                .then(response => {
                    this.getShotCutCarts()
                    alert(this.sku_id)
                })
                .catch(error => {
                    console.log(error.response);
                })
        },
        to_buy(){
            this.isBuy = true
            this.showPanel1 = false
            this.showPanel2 = true
            if (this.isShowSize)
            {
                if (this.color_num == -1 || this.size_num == -1 || this.sku_id == -1)
                {
                    this.showPanel1 = true
                    this.showPanel2 = false
                    return
                }
            }else
            {
                if (this.color_num == -1 || this.sku_id == -1)
                {
                    this.showPanel1 = true
                    this.showPanel2 = false
                    return
                }
            }
            let url = '/buy/';
            axios.post(url, {
                // sku_id: parseInt(this.sku_id),
                // count: this.sku_count,
                specs:this.specs,
            }, {
                headers: {
                    'X-CSRFToken':getCookie('csrftoken')
                },
                responseType: 'json',
                withCredentials: true
            })
                .then(res => {
                    location.href = '/buy?sku_id=' + parseInt(this.sku_id) + '&count=' + this.sku_count +'&specs=' + res.data.specs
                })
                .catch(error => {
                    console.log(error.response);
                })
        },
        showPanel(){
            this.showPanel1 = false
            this.showPanel2 = true
        },
        // // 控制页面标签页展示
        on_tab_content(name){
        //     // this.tab_content = {
        //     //     detail: false,
        //     //     pack: false,
        //     //     comment: false,
        //     //     service: false
        //     // };
        //     // this.tab_content[name] = true;
        },
    	// // 获取热销商品数据
        get_hot_skus(){
        //     // if (this.category_id) {
        //     //     let url = '/hot/'+ this.category_id +'/';
        //     //     axios.get(url, {
        //     //         responseType: 'json'
        //     //     })
        //     //         .then(response => {
        //     //             this.hot_skus = response.data.hot_skus;
        //     //             for(let i=0; i<this.hot_skus.length; i++){
        //     //                 this.hot_skus[i].url = '/detail/' + this.hot_skus[i].id + '/';
        //     //             }
        //     //         })
        //     //         .catch(error => {
        //     //             console.log(error.response);
        //     //         })
        //     // }
        },
        // // 记录分类商品的访问量
		goods_visit_count(){
        // 	// if (this.category_id) {
        // 	// 	let url = '/detail/visit/' + this.category_id + '/';
		// 	// 	axios.post(url, {}, {
        //     //         headers: {
        //     //             'X-CSRFToken':getCookie('csrftoken')
        //     //         },
        //     //         responseType: 'json'
        //     //     })
		// 	// 		.then(response => {
		// 	// 			console.log(response.data);
		// 	// 		})
		// 	// 		.catch(error => {
		// 	// 			console.log(error.response);
		// 	// 		});
		// 	// }
		},
		// // 保存用户浏览记录
		save_browse_histories(){
        // 	// if (this.sku_id) {
        // 	// 	let url = '/browse_histories/';
		// 	// 	axios.post(url, {
        //     //         'sku_id':this.sku_id
        //     //     }, {
        //     //         headers: {
        //     //             'X-CSRFToken':getCookie('csrftoken')
        //     //         },
        //     //         responseType: 'json'
        //     //     })
		// 	// 		.then(response => {
		// 	// 			console.log(response.data);
		// 	// 		})
		// 	// 		.catch(error => {
		// 	// 			console.log(error.response);
		// 	// 		});
		// 	// }
		},

        // // 获取商品评价信息
        get_goods_comment(){
        //     if (this.sku_id) {
        //         let url = '/comments/'+ this.sku_id +'/';
        //         axios.get(url, {
        //             responseType: 'json'
        //         })
        //             .then(response => {
        //                 this.comments = response.data.comment_list;
        //                 for(let i=0; i<this.comments.length; i++){
        //                     this.comments[i].score_class = this.score_classes[this.comments[i].score];
        //                 }
        //             })
        //             .catch(error => {
        //                 console.log(error.response);
        //             });
        //     }
        },

    }
});