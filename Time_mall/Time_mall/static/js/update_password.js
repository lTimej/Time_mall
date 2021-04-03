// 我们采用的时ES6的语法
// 创建Vue对象 vm
let vm = new Vue({
    el: '#app', // 通过ID选择器找到绑定的HTML内容
    // 修改Vue读取变量的语法
    delimiters: ['[[', ']]'],
    data: { // 数据对象
        // v-model


        // v-show


        // error_message

    },
    mounted(){

    },
    methods: { // 定义和实现事件方法
        // 监听表单提交事件
        // on_submit() {
        //     // 在校验之后，注册数据中，只要有错误，就禁用掉表单的提交事件
        //     if (this.error_name == true || this.error_password == true || this.error_password2 == true || this.error_mobile == true || this.error_allow == true || this.error_image_code == true || this.error_sms_code == true) {
        //         // 禁用掉表单的提交事件
        //         window.event.returnValue = false;
        //     }
        // },
    }
});