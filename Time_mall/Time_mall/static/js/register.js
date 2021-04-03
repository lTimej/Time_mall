// 我们采用的时ES6的语法
// 创建Vue对象 vm
let vm = new Vue({
    el: '#app', // 通过ID选择器找到绑定的HTML内容
    // 修改Vue读取变量的语法
    delimiters: ['[[', ']]'],
    data: { // 数据对象
        // v-model
        username: '',
        password: '',
        password2: '',
        mobile: '',
        allow: '',
        img_url: '',
        image_code: '',
        sms_code: '',
        get_sms_code: '获取短信验证码',
        uuid: '',

        // v-show
        error_name: false,
        error_password: false,
        error_password2: false,
        error_mobile: false,
        error_allow: false,
        error_image_code: false,
        error_sms_code : false,

        // error_message
        error_name_message: '',
        error_mobile_message: '',
        error_image_code_message: '',
        error_sms_code_message: '',

        //短信发送标志
        sms_code_flag: false,
        //图片验证码校验标志
        img_code_flag: '',
    },
    mounted(){
        //生成uuid四个
        this.generateCode()
    },
    methods: { // 定义和实现事件方法
        //图片验证码
        generateCode(){
            this.uuid = generateUUID();
            let url = 'http://192.168.1.132:8081/imgCode/' + this.uuid +'/';
            this.img_url = url
        },
        //更换验证码
        changeImg(){
            this.generateCode();
        },
        //校验图片验证码
        check_image_code() {
            if(!this.image_code)
                {
                    this.error_image_code_message = "验证码不为空"
                    this.error_image_code = true
                }
                else{
                    this.error_image_code = false
                }
        },
        //短信验证
        check_sms_code(){
            console.log("进来了")
            if (!this.sms_code)
            {
                this.error_sms_code_message = "不为空";
                this.error_sms_code = true
            }
            else if(this.sms_code.length<6 && this.sms_code.length)
            {
                this.error_sms_code_message = "验证为6位有效字符"
                this.error_sms_code = true
            }else{
                this.error_sms_code = false
            }

        },
        //点击发送短信验证码
        sendSmsCode() {
            //避免重复发送
            if(this.sms_code_flag)
            {
                return
            }
            this.sms_code_flag = true;
            this.check_image_code();
            this.check_mobile();
            //如果手机号和图片验证码错误可以继续点击发送
            if (this.error_mobile || this.error_image_code)
            {
                this.sms_code_flag = false;
                return
            }
            let sms_code_url = 'http://192.168.1.132:8081/smsCode/' + this.mobile + '?uuid=' +this.uuid +'&img_code=' + this.image_code
            axios.get(sms_code_url,{
                responseType:"json"
            }).then(res=>{
                if (res.data.code == '0')
                {
                    let num = 60 ;
                    this.get_sms_code =  res.data.errmsg
                    //倒计时操作
                    let timer = setInterval(()=>{
                        num--
                        if (num<=0)
                        {//倒计时结束
                            this.get_sms_code = '获取短信验证码'
                            this.sms_code_flag = false;
                            clearInterval(timer)
                            return
                        }
                        this.get_sms_code = String(num) + ' 秒'
                    },1000)
                }
                else
                {
                    if(res.data.code == '4001')
                    {//验证码失效
                        console.log("验证码失效")
                        this.error_image_code_message = res.data.errmsg
                        this.error_image_code = true
                    }
                    else{//验证码错误  4002  4003
                        console.log("验证码错误")
                        this.error_image_code_message = res.data.eerrmsg
                        this.error_image_code = true
                    }
                    //验证码出现错误，产生新的的验证码
                    this.sms_code_flag = false
                    this.generateCode();
                }
            }).catch(error=>{
                //错误
                this.sms_code_flag = false
            })
        },
        // 校验用户名
        check_username() {
            // 用户名是5-20个字符，[a-zA-Z0-9_-]
            // 定义正则
            let re = /^[a-zA-Z0-9_-]{4,16}$/;
            // 使用正则匹配用户名数据
            if (re.test(this.username)) {
                // 匹配成功，不展示错误提示信息
                this.error_name = false;
            } else {
                // 匹配失败，展示错误提示信息
                this.error_name_message = '请输入4-16个字符的用户名';
                this.error_name = true;
            }
            //用户名重复校验
            if(this.error_name == false){
                axios.get('http://192.168.1.132:8081/userUnique/'+this.username+'/',{
                    responseType:'json'
                }).then(res=>{
                    if (res.data.count != 0)
                    {
                        this.error_name_message = '用户名已被注册';
                        this.error_name = true;
                    }
                })
            }
        },
        // 校验密码
        check_password() {
            let re = /^[0-9A-Za-z]{8,16}$/;
            if (re.test(this.password)) {
                this.error_password = false;
            } else {
                this.error_password = true;
            }
        },
        // 校验确认密码
        check_password2() {
            if (this.password != this.password2) {
                this.error_password2 = true;
            } else {
                this.error_password2 = false;
            }
        },
        // 校验手机号
        check_mobile() {
            let re = /^1[3-9]\d{9}$/;
            if (re.test(this.mobile)) {
                this.error_mobile = false;
            } else {
                this.error_mobile_message = '您输入的手机号格式不正确';
                this.error_mobile = true;
            }
            //手机号重复校验
            if(this.error_mobile == false){
                axios.get('http://192.168.1.132:8081/phone/'+this.mobile+'/',{
                    responseType:'json'
                }).then(res=>{
                    if (res.data.count != 0)
                    {
                        this.error_mobile_message = '手机号已被注册';
                        this.error_mobile = true;
                    }
                })
            }
        },
        // 校验是否勾选协议
        check_allow() {
            if (!this.allow) {
                this.error_allow = true;
            } else {
                this.error_allow = false;
            }
        },
        // 监听表单提交事件
        on_submit() {
            this.check_username();
            this.check_password();
            this.check_password2();
            this.check_mobile();
            this.check_allow();
            this.check_image_code();
            this.check_sms_code();

            // 在校验之后，注册数据中，只要有错误，就禁用掉表单的提交事件
            if (this.error_name == true || this.error_password == true || this.error_password2 == true || this.error_mobile == true || this.error_allow == true || this.error_image_code == true || this.error_sms_code == true) {
                // 禁用掉表单的提交事件
                window.event.returnValue = false;
            }
        },
    }
});