let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: getCookie('username'),
        trade_id:trade_id

    },
    //界面刷新完成执行
    mounted() {

    },

    //方法
    methods: {

}
});