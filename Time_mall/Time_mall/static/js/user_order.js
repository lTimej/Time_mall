let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: getCookie('username'),
        page_num:page_num,
        total_page:total_page,
        orders:JSON.parse(JSON.stringify(orders))

    },
    //界面刷新完成执行
    mounted() {

    },

    //方法
    methods: {

}
});