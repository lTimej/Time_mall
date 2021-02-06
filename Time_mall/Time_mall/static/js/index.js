let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: '',
    },
    mounted(){
        //获取cookie
        this.username = getCookie("username")
    }

    ,
    methods: {

    }
});