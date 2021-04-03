import json,re,scrapy

from GoodsData.utils import writeDataBase,verdict

class IndexSpider(scrapy.Spider):
    '''
    抓取首页数据
    '''
    name = 'goodsInfo'
    allowed_domains = ['market.mogu.com']
    start_urls = ['https://api.mogu.com/h5/mwp.darwin.multiget/3/?data=%7B%22pids%22%3A%22132244%2C138852%2C138851%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1615624360676&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=c47bdc67ece4f16c4633b17de4894f43&callback=mwpCb1&_=1615624360683',
                'https://api.mogu.com/h5/mwp.darwin.multiget/3/?data=%7B%22appPlat%22%3A%22p%22%2C%22pids%22%3A%22110521%2C110523%2C110564%2C60357%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1615624360803&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=e6f78b3e99a2880d0d60c3ae5c07dd83&callback=mwpCb2&_=1615624360819',
                'https://api.mogu.com/h5/mwp.ferrari.searchActionLet/1/?data=%7B%22page%22%3A1%2C%22pageSize%22%3A36%2C%22activityLaunchId%22%3A%221266%22%2C%22code%22%3A%22itemPageList%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1615624360876&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=16126b922893fac5a145a8004588b687&callback=mwpCb3&_=1615624360881',
                'https://api.mogu.com/h5/mwp.darwin.multiget/3/?data=%7B%22appPlat%22%3A%22p%22%2C%22pids%22%3A%22110528%2C110535%2C110759%2C110843%2C110892%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1615624361369&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=b4b9b4fb82decd3ea04373f1016d1ca2&callback=mwpCb5&_=1615624361371',
                'https://api.mogu.com/h5/mwp.darwin.multiget/3/?data=%7B%22appPlat%22%3A%22p%22%2C%22pids%22%3A%22110538%2C110542%2C110845%2C110847%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1615624363423&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=86b4fd80e67a9b9b30d4f2026f962d8f&callback=mwpCb6&_=1615624363427',
                'https://mce.mogucdn.com/jsonp/multiget/3?appPlat=p&pids=109514%2C110449%2C110456%2C110468%2C30799&callback=jsonp109514_110449_110456_110468_30799&_=1615624360829']
    def start_requests(self):  # 重构start_requests方法
        # cookies_str是request_header抓包获取的
        cookies_str = '__mgjuuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9; _ga=GA1.2.970001936.1612227271; smidV2=20210202094430031611518b87722548ae4b71ccfe721b003914682dd14eb00; _mwp_h5_token=a000922c451c16333e8faffd38de447a_1615604325175; _mwp_h5_token_enc=27034531b700c5559e0fb675c4d83fb3; _gid=GA1.2.1829590315.1615604326; mf_cache=Hg_szVQ4QlmEIYLfSiU5MQ; FRMS_FINGERPRINTN=Hg_szVQ4QlmEIYLfSiU5MQ; __mogujie=SgUuMwdoejrXW2Cd4EcQ0Fh6XOLx7eX6gxpJ8EHeyLuV7jKOGyUYcRDVQkQyZGuWF4Rjet2HXr9Bx%2FTKFUfAdw%3D%3D; __ud_=1fgw9dy; __mgjref=http%3A%2F%2Fwww.mogujie.com%2F; __must_from=70000000_; _gat=1'  # 抓包获取
        # 将cookies_str转换为cookies_dict
        cookies_dict = {i.split('=')[0]: i.split('=')[1] for i in cookies_str.split('; ')}
        #添加头文件，不添加会获取不到文件
        headers = {
            'referer': 'https://market.mogu.com/'
        }
        for i in range(len(self.start_urls)):
            yield scrapy.Request(
                self.start_urls[i],
                callback=self.parse,
                cookies=cookies_dict,
                headers=headers
            )
    def parse(self,response):
        res = response.text
        #转换称字典
        data_str = re.search('\((.+)\)', res).group(1)
        data_dict = json.loads(data_str)
        data = data_dict.get('data')
        try:#解析数据
            for pid, values in data.items():
                for index,goods in enumerate(values.get('list'),1):
                    title = goods.get('title')
                    link = goods.get('link')
                    if not link:
                        link = goods.get('item_url')
                    image = goods.get('image')
                    if not image:
                        image = None
                    price = goods.get('discountPrice')
                    #判断数据为首页哪一个板块
                    verdict(goods,title,link,pid,image,index,price)
        except:#数据解析方式不同进入
            for index,goods in enumerate(data.get('list'),1):
                title = goods.get('title')
                link = 'https:' + goods.get('link')
                image = goods.get('image')
                price = goods.get('price')
                discountprice = goods.get('salePrice')
                # 保存数据库逻辑
                writeDataBase('今日必抢', title,'10000', link, image, index, price,discountprice=discountprice)


'''
['https://api.mogu.com/h5/mwp.darwin.multiget/3/?data=%7B%22pids%22%3A%22132244%2C138852%2C138851%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1614265211009&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=178ff4a38cdb00d040a3cc1f1bfea8a9&callback=mwpCb1&_=1614265211015',

'https://api.mogu.com/h5/mwp.darwin.multiget/3/?data=%7B%22appPlat%22%3A%22p%22%2C%22pids%22%3A%22110538%2C110542%2C110845%2C110847%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1614216490458&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=9b3712bf93b47f751c2ad33d200a8eda&callback=mwpCb6&_=1614216490464',
                  
'https://api.mogu.com/h5/mwp.darwin.multiget/3/?data=%7B%22appPlat%22%3A%22p%22%2C%22pids%22%3A%22110528%2C110535%2C110759%2C110843%2C110892%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1614214400282&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=b0b45792afb04dd890bb37caaec984d7&callback=mwpCb5&_=1614214400284',
                  
'https://api.mogu.com/h5/mwp.darwin.multiget/3/?data=%7B%22appPlat%22%3A%22p%22%2C%22pids%22%3A%22110521%2C110523%2C110564%2C60357%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1614214399747&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=8d05dd33f87b3aaa9d5e36e1a14d1d20&callback=mwpCb2&_=1614214399750',
                  
'https://mce.mogucdn.com/jsonp/multiget/3?appPlat=p&pids=109514%2C110449%2C110456%2C110468%2C30799&callback=jsonp109514_110449_110456_110468_30799&_=1614221977050',
                  
'https://api.mogu.com/h5/mwp.ferrari.searchActionLet/1/?data=%7B%22page%22%3A1%2C%22pageSize%22%3A36%2C%22activityLaunchId%22%3A%221266%22%2C%22code%22%3A%22itemPageList%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1614221977101&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=80e86135b89a90a54d9bb4a97f64ed82&callback=mwpCb3&_=1614221977103']
                  
 --------------------------------         
 主题        
https://api.mogu.com/h5/mwp.darwin.multiget/3/?data=%7B%22pids%22%3A%22132244%2C138852%2C138851%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1615615527646&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=c8b135512c81e98b5901835c3e1f1cc0&callback=mwpCb1&_=1615615527655
女鞋包包  女装
https://api.mogu.com/h5/mwp.darwin.multiget/3/?data=%7B%22appPlat%22%3A%22p%22%2C%22pids%22%3A%22110521%2C110523%2C110564%2C60357%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1615615527775&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=37cf15739f19159816bc3a9a994b5e4d&callback=mwpCb2&_=1615615527779
每日推荐
https://api.mogu.com/h5/mwp.ferrari.searchActionLet/1/?data=%7B%22page%22%3A1%2C%22pageSize%22%3A36%2C%22activityLaunchId%22%3A%221266%22%2C%22code%22%3A%22itemPageList%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1615615527828&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=c77bd686b4d6c4a27de9ea2f875c0d90&callback=mwpCb3&_=1615615527832
女鞋包包推荐 内衣推荐 男装男鞋 男装推荐  内衣
https://api.mogu.com/h5/mwp.darwin.multiget/3/?data=%7B%22appPlat%22%3A%22p%22%2C%22pids%22%3A%22110528%2C110535%2C110759%2C110843%2C110892%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1615616040795&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=6c54f3b0082fa60dc708ef06608afb18&callback=mwpCb5&_=1615616040801
限时快抢
https://mce.mogucdn.com/jsonp/multiget/3?appPlat=p&pids=109514%2C110449%2C110456%2C110468%2C30799&callback=jsonp109514_110449_110456_110468_30799&_=1615615527784


'''
'''

https://api.mogu.com/h5/mwp.darwin.multiget/3/?data=%7B%22appPlat%22%3A%22p%22%2C%22pids%22%3A%22110538%2C110542%2C110845%2C110847%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1615624363423&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=86b4fd80e67a9b9b30d4f2026f962d8f&callback=mwpCb6&_=1615624363427
休闲男装
https://api.mogu.com/h5/mwp.darwin.multiget/3/?data=%7B%22appPlat%22%3A%22p%22%2C%22pids%22%3A%22110528%2C110535%2C110759%2C110843%2C110892%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1615624361369&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=b4b9b4fb82decd3ea04373f1016d1ca2&callback=mwpCb5&_=1615624361371
每日推荐
https://api.mogu.com/h5/mwp.ferrari.searchActionLet/1/?data=%7B%22page%22%3A1%2C%22pageSize%22%3A36%2C%22activityLaunchId%22%3A%221266%22%2C%22code%22%3A%22itemPageList%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1615624360876&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=16126b922893fac5a145a8004588b687&callback=mwpCb3&_=1615624360881
女鞋
https://api.mogu.com/h5/mwp.darwin.multiget/3/?data=%7B%22appPlat%22%3A%22p%22%2C%22pids%22%3A%22110521%2C110523%2C110564%2C60357%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1615624360803&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=e6f78b3e99a2880d0d60c3ae5c07dd83&callback=mwpCb2&_=1615624360819

主题
https://api.mogu.com/h5/mwp.darwin.multiget/3/?data=%7B%22pids%22%3A%22132244%2C138852%2C138851%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1615624360676&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=c47bdc67ece4f16c4633b17de4894f43&callback=mwpCb1&_=1615624360683

https://mce.mogucdn.com/jsonp/multiget/3?appPlat=p&pids=109514%2C110449%2C110456%2C110468%2C30799&callback=jsonp109514_110449_110456_110468_30799&_=1615624360829
'''
'''
['https://api.mogu.com/h5/mwp.darwin.multiget/3/?data=%7B%22pids%22%3A%22132244%2C138852%2C138851%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1615624360676&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=c47bdc67ece4f16c4633b17de4894f43&callback=mwpCb1&_=1615624360683',
'https://api.mogu.com/h5/mwp.darwin.multiget/3/?data=%7B%22appPlat%22%3A%22p%22%2C%22pids%22%3A%22110521%2C110523%2C110564%2C60357%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1615624360803&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=e6f78b3e99a2880d0d60c3ae5c07dd83&callback=mwpCb2&_=1615624360819',
'https://api.mogu.com/h5/mwp.ferrari.searchActionLet/1/?data=%7B%22page%22%3A1%2C%22pageSize%22%3A36%2C%22activityLaunchId%22%3A%221266%22%2C%22code%22%3A%22itemPageList%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1615624360876&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=16126b922893fac5a145a8004588b687&callback=mwpCb3&_=1615624360881',
'https://api.mogu.com/h5/mwp.darwin.multiget/3/?data=%7B%22appPlat%22%3A%22p%22%2C%22pids%22%3A%22110528%2C110535%2C110759%2C110843%2C110892%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1615624361369&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=b4b9b4fb82decd3ea04373f1016d1ca2&callback=mwpCb5&_=1615624361371',
'https://api.mogu.com/h5/mwp.darwin.multiget/3/?data=%7B%22appPlat%22%3A%22p%22%2C%22pids%22%3A%22110538%2C110542%2C110845%2C110847%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=1615624363423&mw-uuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9&mw-h5-os=unknown&mw-sign=86b4fd80e67a9b9b30d4f2026f962d8f&callback=mwpCb6&_=1615624363427',
'https://mce.mogucdn.com/jsonp/multiget/3?appPlat=p&pids=109514%2C110449%2C110456%2C110468%2C30799&callback=jsonp109514_110449_110456_110468_30799&_=1615624360829']
'''