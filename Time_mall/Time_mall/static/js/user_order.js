let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: username,
        mobile: mobile,
        email: email,
        email_active: email_active,

        set_email: true,
        error_email: false,

        send_email_btn_disabled: false,
        send_email_tip: '重新发送验证邮件',
        histories: [],
    },
    //界面刷新完成执行
    mounted() {
        //后端传来的email_active为"False"将其转为js的true
        this.email_active = (this.email_active == 'True') ? true:false
        //如果邮箱验证成果则显示待验证或已验证
        this.set_email = (this.email)?false:true
    },

    //方法
    methods: {
        //保存邮箱
        save_email()
        {
            //发送之前检验email格式
            this.check_email()
            if (this.error_email)
            {
                this.error_email = true
                return
            }
            this.set_email = false
            this.email_active = false
            let url = '/email/'
            axios.put(url,{//参数
                "email":this.email,
            },{
                headers:{'X-CSRFToken':getCookie('csrftoken')},
                responseType:'json'
            }).then(res=>{
                if (res.data.code == '0')
                {
                    this.send_email_tip = res.data.errmsg
                    send_email_btn_disabled = true
                }
            }).catch(err=>{
                console.log(err);
            })
        },
        //邮箱验证
        check_email()
        {
            let re = /^[0-9a-zA-Z]{1,16}@(qq||yeah||126||163)\.(net||cn||com)$/
            if (re.test(this.email) && this.email){//符合邮箱格式并且不为空，则不展示错误提示信息
                this.error_email = false
            }else{
                this.error_email = true
            }
        },
        //取消邮箱保存
        cancel_email()
        {

        },



    }
});