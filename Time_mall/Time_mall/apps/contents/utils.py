from goods.models import GoodsCategory,ProductId
from django.conf import settings

htt = settings.HTT
htts = settings.HTTS
def get_category():
    '''
    获取商品分类
    :return: 商品分类信息
    '''
    goods = dict()
    #获取商品类别
    categories = GoodsCategory.objects.filter(parent_id__isnull=True)
    #构造分类信息
    for category in categories:
        #商品一级分类
        obj = category.goodslist_set.get()
        ppid = ProductId.objects.get(id=obj.pid_id)
        pid = ppid.pid
        goods[pid] = {}
        goods[pid]['id'] = obj.category_id
        goods[pid]['name'] = obj.category.name
        goods[pid]['url'] = ''
        goods[pid]['subs'] = []
        #商品二级分类
        for subs in category.subs.all()[0:3]:
            if subs.name == '帽子':#这里只开发出帽子这一类别商品
                category_id = subs.id
                url = htts + 'goodslist/' + str(category_id)#待优化
            else:
                url = "#"
            goods[pid]['subs'].append({
                'id': subs.id,
                'name': subs.name,
                'url':url
            })
    #返回主题分类信息
    return goods
data1,data2,data3,data4,data5,data6,data7,data33,data44,data55,data66,data77 = [],[],[],[],[],[],[],[],[],[],[],[]
def get_data(cc_title,title,price,discountprice,image):
    '''
    #构造首页商品广告楼层信息
    :param cc_title: 二级类别名称
    :param title: 分类内容商品名称
    :param price: 商品价格
    :param discountprice: 商品折后价格
    :param image: 商品图片
    '''
    if cc_title == '今日必抢':
        today_grab = {
            "title": title,
            "price": float(price),
            "discountprice": float(discountprice),
            "image": htt + str(image)
        }
        data1.append(today_grab)
    elif cc_title == "女装":
        woman_cloth = {
            "title": title[0:10] +'...',
            "price": float(price),
            "image": htt + str(image)
        }
        data2.append(woman_cloth)
    elif cc_title.strip() == '女鞋&包包':
        woman_shoe = {
        "title": title[0:10] + '...',
        "price": float(price),
        "image": htt + str(image)
        }
        data3.append(woman_shoe)
    elif cc_title == '女鞋&包包 推荐':
        woman_shoe_recomm = {
            "title": title[0:18] + '...',
            "price": float(price),
            "image": htt + str(image)
        }
        data33.append(woman_shoe_recomm)
    elif cc_title.strip() == '男装&男鞋':
        man_shoe = {
        "title": title[0:10] + '...',
        "price": float(price),
        "image": htt + str(image)
        }
        data4.append(man_shoe)
    elif cc_title == '男装&男鞋 推荐':
        man_shoe_recomm = {
            "title": title[0:18] + '...',
            "price": float(price),
            "image": htt + str(image)
        }
        data44.append(man_shoe_recomm)
    elif cc_title.strip() == '内衣':
        underWare = {
        "title": title[0:10] + '...',
        "price": float(price),
        "image": htt + str(image)
        }
        data5.append(underWare)
    elif cc_title == '内衣 推荐':
        underWare_recomm = {
            "title": title[0:18] + '...',
            "price": float(price),
            "image": htt + str(image)
        }
        data55.append(underWare_recomm)
    elif cc_title.strip() == '家纺&家饰':
        home_textile = {
        "title": title[0:10] + '...',
        "price": float(price),
        "image": htt + str(image)
        }
        data6.append(home_textile)
    elif cc_title == '家纺&家饰 推荐':
        jiaju_recomm = {
            "title": title[0:18] + '...',
            "price": float(price),
            "image": htt + str(image)
        }
        data66.append(jiaju_recomm)
    elif cc_title.strip() == '母装&儿童':
        mvying = {
        "title": title[0:10] + '...',
        "price": float(price),
        "image": htt + str(image)
        }
        data7.append(mvying)
    elif cc_title == '母装&儿童 推荐':
        mvying_recomm = {
            "title": title[0:18] + '...',
            "price": float(price),
            "image": htt + str(image)
        }
        data77.append(mvying_recomm)
def get_contents(contents):
    '''
    获取首页广告楼层信息
    :param contents: 广告内容对象
    :return:
    '''
    contents['today_grab'] = []
    contents['woman_cloth'] = []
    contents['woman_shoe'] = []
    contents['woman_shoe_recomm'] = []
    contents['man_shoe'] = []
    contents['man_shoe_recomm'] = []
    contents['underWare'] = []
    contents['underWare_recomm'] = []
    contents['home_textile'] = []
    contents['jiaju_recomm'] = []
    contents['mvying'] = []
    contents['mvying_recomm'] = []
    for i in range(0, len(data1), 4):
        d = [k for k in data1[i:i + 4]]
        contents['today_grab'].append(d)
    for i in range(0, len(data2), 4):
        d = [k for k in data2[i:i + 4]]
        contents['woman_cloth'].append(d)
    for i in range(0, len(data3), 6):
        d = [k for k in data3[i:i + 6]]
        contents['woman_shoe'].append(d)
    for i in range(0, len(data33), 4):
        d = [k for k in data33[i:i + 4]]
        contents['woman_shoe_recomm'].append(d)
    for i in range(0, len(data4), 6):
        d = [k for k in data4[i:i + 6]]
        contents['man_shoe'].append(d)
    for i in range(0, len(data44), 4):
        d = [k for k in data44[i:i + 4]]
        contents['man_shoe_recomm'].append(d)
    for i in range(0, len(data5), 6):
        d = [k for k in data5[i:i + 6]]
        contents['underWare'].append(d)
    for i in range(0, len(data55), 4):
        d = [k for k in data55[i:i + 4]]
        contents['underWare_recomm'].append(d)
    for i in range(0, len(data6), 6):
        d = [k for k in data6[i:i + 6]]
        contents['home_textile'].append(d)
    for i in range(0, len(data66), 4):
        d = [k for k in data66[i:i + 4]]
        contents['jiaju_recomm'].append(d)
    for i in range(0, len(data7), 6):
        d = [k for k in data7[i:i + 6]]
        contents['mvying'].append(d)
    for i in range(0, len(data77), 4):
        d = [k for k in data77[i:i + 4]]
        contents['mvying_recomm'].append(d)