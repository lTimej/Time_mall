let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: getCookie('username'),
        is_show_edit: false,
        form_address: {//保存新增框或者修改框的数据
            receiver: '',
            province_id: '',
            city_id: '',
            district_id: '',
            place: '',
            mobile: '',
            tel: '',
            email: '',
        },

        provinces: [],
        cities: [],
        districts: [],
        addresses:JSON.parse(JSON.stringify(addresses1)),
        default_address_id: default_address_id,
        editing_address_index: '',
        edit_title_index: '',
        new_title: '',

        error_receiver: false,
        error_place: false,
        error_mobile: false,
        error_tel: false,
        error_email: false,

        error_title_msg:''
    },
    //页面加载完成执行
    mounted(){
        this.get_province_data()
    },
    //方法
    methods:{
        get_province_data()
        {//获取省份数据
            let url = '/areas/'
            axios.get(url,{
                responseType:"json"
            }).then(res=>{
                if (res.data.code=='0')
                {
                    this.provinces = res.data.province_list
                }else{
                    this.provinces = []
                }
            }).catch(err=>{
                console.log(err);
            })
        },
        //清空form_address
        clear_form_address()
        {
            this.form_address.receiver = '';
            this.form_address.province_id = '';
            this.form_address.city_id = '';
            this.form_address.district_id = '';
            this.form_address.place = '';
            this.form_address.mobile = '';
            this.form_address.tel = '';
            this.form_address.email = '';
            this.editing_address_index = '';
        },
        //添加地址
        add_address()
        {

            this.clear_error_msg()
            this.clear_form_address()
            this.is_show_edit = true
        },
        //展现编辑框
        show_edit_site(index)
        {
            this.is_show_edit = true
            this.clear_error_msg()
            this.form_address = JSON.parse(JSON.stringify(this.addresses[index]))
            this.form_address.province_id = this.addresses[index].province_id
            this.form_address.city_id = this.addresses[index].city_id
            this.form_address.district_id= this.addresses[index].district_id
            this.editing_address_index = index.toString();
        },
        //新增地址
        save_address()
        {
            this.check_receiver();
            this.check_place();
            this.check_mobile();
            this.check_tel();
            this.check_email()
            // 在校验之后，注册数据中，只要有错误，就禁用掉表单的提交事件
            if (this.error_receiver==true || this.error_place==true || this.error_mobile==true || this.error_tel==true || this.error_email==true)
            {
                // 禁用掉表单的提交事件
                window.event.returnValue = false;
            }else{
                if (this.editing_address_index === '')
                {//增加地址
                    let url = '/address/add/'
                axios.post(url,this.form_address,
                    {
                        headers: {'X-CSRFToken':getCookie('csrftoken')},
                        responseType:'json'
                    }).then(res=>{
                    if (res.data.code=='0')
                    {
                        this.addresses.splice(0, 0, res.data.address_dict);
                        this.is_show_edit = false;
                        location.href = '/address/'
                    }else if(res.data.code == '5000'){//未登录返回登录页面
                        location.href = '/login/?next=/address/';
                    }else{//地址总数超过20,报错
                        alert(res.data.errmsg)
                    }
                }).catch(err=>{
                    console.log(err);
                })
                }
                else{//修改地址
                    let url = '/address/update/' + this.addresses[this.editing_address_index].id +'/'
                    axios.put(url,this.form_address,
                    {
                        headers: {'X-CSRFToken':getCookie('csrftoken')},
                        responseType:'json'
                    }).then(res=>{
                        console.log(res);
                        if (res.data.code=='0')
                        {
                            this.addresses[this.editing_address_index] = res.data.address_dict;
                            this.is_show_edit = false;
                        }else{//未登录返回登录页面
                            location.href = '/login/?next=/address/';
                        }
                    }).catch(err=>{
                        console.log(err);
                    })
                }
            }
        },
        //校验收件人
        check_receiver()
        {
            //不为空
            if (!this.form_address.receiver)
            {
                this.error_receiver = true
            }else{
                this.error_receiver =false
            }
        },
        //校验收件地址
        check_place()
        {
            //不为空
            if (!this.form_address.place)
            {
                this.error_place = true
                return
            }
            this.error_place = false
        },
        //校验手机号
        check_mobile()
        {
            let re = /^1[3-9]\d{9}$/;
            if (re.test(this.form_address.mobile))
            {
                this.error_mobile =false
            }else{
                this.error_mobile =true
            }
        },
        //校验固定电话
        check_tel()
        {
            if (!this.form_address.tel)
            {
                return;
            }
            let re = /^[0-9]{7}$/;
            if (!re.test(this.form_address.mobile))
            {
                this.error_tel =true
            }else{
                this.error_tel =false
            }
        },
        //校验邮箱
        check_email()
        {
            if (!this.form_address.email)
            {
                return;
            }
            let re = /^[0-9a-zA-Z]{1,16}@(qq||yeah||126||163)\.(net||cn||com)$/
            if (!re.test(this.form_address.email))
            {
                this.error_email =true
            }else{
                this.error_email =false
            }

        },
        //校验标题修改
        check_update_title(){
            if (!this.new_title)
            {
                this.error_title_msg = "标题不为空"
                return
            }
            this.error_title_msg = ''
        },
        //设置默认地址
        set_default(index)
        {
            let url = '/set/default/address/' + this.addresses[index].id +'/'
            axios.put(url,{},{
                headers: {
                    'X-CSRFToken':getCookie('csrftoken')
                },
                responseType: 'json'
            }).then(res=>{
                console.log(res);
                if (res.data.code == '0')
                {
                    // 设置默认地址标签
                        this.default_address_id = this.addresses[index].id;
                }else{
                    location.href = '/login/?next=/addresses/';
                }
            }).catch(err=>{
                console.log(err);
            })
        },
        //清除错误信息
        clear_error_msg()
        {
            this.error_receiver = false
            this.error_place = false
            this.error_mobile = false
            this.error_tel = false
            this.error_email = false
        },
        //删除地址
        delete_address(index)
        {
            let url = '/address/del/' +this.addresses[index].id
            axios.delete(url,{
                headers: {'X-CSRFToken':getCookie('csrftoken')},
                responseType:'json'
            }).then(res=>{
                console.log(res);
                if (res.data.code == '0')
                {
                    // 删除对应的标签
                    this.addresses.splice(index, 1);
                }else{//没有登录的情况下删除失败，返回登录页面
                    location.href = '/login/?next=/address/';
                }
            }).catch(err=>{
                console.log(err);
            })
        },
        //查看标题编辑框
        show_edit_title(index)
        {
            this.edit_title_index = index
        },
        //取消保存标题
        cancel_title(index)
        {
            this.edit_title_index = ''
            this.error_title_msg = ''
        },
        //保存标题
        save_title(index,iid)
        {
            this.check_update_title();
            if (this.error_title_msg)
            {
                return
            }
            let url = '/address/update/title/' + iid + '/'
            axios.put(url,data={
                new_title:this.new_title,
            },
            {
                headers: {'X-CSRFToken':getCookie('csrftoken')},
                responseType:'json'
            }).then(res=>{
                console.log(res);
                if (res.data.code == '0')
                {
                    this.addresses[index].title = this.new_title
                    this.edit_title_index = ''
                    this.new_title = ''
                    this.error_title_msg = ''
                }else{//没登录返回登录页面
                    location.href = '/login/?next=/address/';
                }
            }).catch(err=>{
                console.log(err);
                this.edit_title_index = ''
                this.new_title = ''
                this.error_title_msg = ''
            })
        }
    },
    watch:{//监听省份id，一旦选中某个省份，就立即执行，获取市级
        "form_address.province_id" :function () {
            if (this.form_address.province_id)
            {
                let url = '/areas/?areas_id=' + this.form_address.province_id
                axios.get(url,{
                    responseType: 'json'
                }).then(res=>{
                    if (res.data.code=='0')
                    {
                        this.cities = res.data.sub_city_list
                    }else{
                        this.cities = []
                    }
                })
            }else{
                this.cities = []
            }
        },//监听市id，一旦选中某个市，就立即执行，获取县级
        "form_address.city_id" :function () {
            if (this.form_address.city_id)
            {
                let url = '/areas/?areas_id=' + this.form_address.city_id
                axios.get(url,{
                    responseType: 'json'
                }).then(res=>{
                    if (res.data.code=='0')
                    {
                        this.districts= res.data.sub_city_list
                    }else{
                        this.districts= []
                    }
                })
            }else{
                this.districts= []
            }
        }
    }
});