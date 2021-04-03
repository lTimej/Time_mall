let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: '',
        myImgFlag:0,
        myImg1:'../static/images/banner0301.png',
        myImg2:'../static/images/banner0302.png',
        myImg3:'../static/images/banner0501.png',
        myImg4:'../static/images/banner0502.png',
        goods:JSON.parse(JSON.stringify(goods)),
        contents:JSON.parse(JSON.stringify(contents)),
        cartss:[],
        cartLen:0
    },
    mounted(){
        //获取快捷栏购物车
        this.getShotCutCarts();
        //获取cookie
        this.username = getCookie("username")
        setInterval(()=>{
            if(this.myImgFlag == 0)
            {
                this.myImgFlag = 1;
            }
            else if(this.myImgFlag == 1){
                this.myImgFlag = 0
            }
        },3000)
    },
    methods: {
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