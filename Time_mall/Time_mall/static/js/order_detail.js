let vm = new Vue({
    el:"#app",
    delimiters: ['[[', ']]'],
    data:{
        username: getCookie('username'),
        cartss:[],
        cartLen:0,
        order : JSON.parse(JSON.stringify(order)),
        address : JSON.parse(JSON.stringify(address)),
        sku : JSON.parse(JSON.stringify(sku)),
    },
    mounted(){
        this.getShotCutCarts();
    },
    methods:{
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
        }
    }
})