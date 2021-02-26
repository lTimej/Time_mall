import sys

import scrapy,re,json

from GoodsData.pipelines import ProductId,GoodsCategory,GoodsList,Spu,SpuSpecs,SpecsOption,Sku,SkuImag,FastFdfs,DetailImag,SkuSpecification
from GoodsData.utils import getGoodsDetailInfo

class HomepageSpider(scrapy.Spider):
    '''
    抓取商品数据
    '''
    name = 'homePage'
    start_urls = [
        'https://mce.mogucdn.com/jsonp/multiget/3?pids=109499%2C109520%2C109731%2C109753%2C110549%2C109779%2C110547%2C109757%2C109793%2C109795%2C110563%2C110546%2C110544']

    def start_requests(self):  # 重构start_requests方法
        cookies_str = '__mgjuuid=8b5db0da-667c-4421-95a1-d8d83b1f36d9; _ga=GA1.2.970001936.1612227271; smidV2=20210202094430031611518b87722548ae4b71ccfe721b003914682dd14eb00; _mwp_h5_token=bf747c3612ddcf60aea979211255b865_1614045286222; _mwp_h5_token_enc=218cac90b71883aaae8cb999f1d3ccf3; _gid=GA1.2.521304411.1614045297; FRMS_FINGERPRINTN=4693DuYZQImnPvECl7RiOg; __mogujie=QkbiDjNf%2BzhpBSdjfEKbzGJwYL4OJiGOM9BN3gijn3i%2F3xhZ6vShATXxNRYy2VOe2Cbre8NxzcUMjv5kpDQrDw%3D%3D; __ud_=1fgw9dy; __must_from=70000000_; _gat=1'
        self.cookies_dict = {i.split('=')[0]: i.split('=')[1] for i in cookies_str.split('; ')}
        headers = {
            'referer': 'https://market.mogu.com/'
        }
        for i in range(len(self.start_urls)):
            yield scrapy.Request(
                self.start_urls[i],
                callback=self.parse,
                headers=headers,
                cookies=self.cookies_dict
            )
    def parse(self, response):
        data = response.text
        index = data.find('(')
        data_str = data[index + 1:-1]
        data_dict = json.loads(data_str)
        data = data_dict.get('data')
        parentId = 1
        categoryId = 0
        for indey, dic in enumerate(data.items(), 1):
            # productId表
            pid = dic[0]
            menus = dic[1]
            ProductId().insert(pid)  # -----------------------------------productId表
            msg = ProductId().select(pid)
            if msg:
                if msg[0]:
                    pid_id = msg[0]
            for index, list in enumerate(menus.get('list'), 1):
                title = list.get('title')
                # 商品分类
                if index == 1:
                    GoodsCategory().insert(title)  # -----------------------------------goods_category表
                    sequeue = 1
                    msg = GoodsCategory().select(title)
                    if msg:
                        if msg[-1][0]:
                            parentId = msg[-1][0]
                            categoryId = msg[-1][0]
                else:
                    GoodsCategory().insert(title, parentId)  # -----------------------------------goods_category表
                    sequeue = index - 1
                    msg = GoodsCategory().select(title)
                    if msg:
                        if msg[-1][0]:
                            parentId = msg[-1][1]
                            categoryId = msg[-1][0]
                link = list.get('link')
                GoodsList().insert(link, sequeue, categoryId, pid_id)  # -----------------------------------goods_list表
                fcid = re.search('^.+/(\d+)?.*', link).groups()[0]
                goods_url_list = 'https://list.mogu.com/search?cKey=15&fcid=' + fcid
                if title == "帽子":
                    yield scrapy.Request(url=goods_url_list, callback=self.goods_list,
                                         meta={'pid': pid, 'title': title, 'category_id': categoryId, "flag": 1})
    def goods_list(self, response):
        category_id = response.meta.get('category_id')
        msg = GoodsCategory().select(category_id=category_id)  # --------------------------------goodcategory查询
        if msg:
            if msg[-1][0]:
                parent_id = msg[-1][0]
            if not msg[-1][0]:
                parent_id = category_id
        data_str = response.text
        data_dict = json.loads(data_str)
        results = data_dict.get('result').get('wall').get('docs')
        for res in results:
            iid = res.get('tradeItemId')
            spu_name = res.get('title')
            Spu().insert(spu_name, parent_id, category_id)  # ------------------------------spu表
            url = getGoodsDetailInfo(iid, self.cookies_dict)
            yield scrapy.Request(url=url, callback=self.detail,
                                 meta={'spu_name': spu_name},
                                 cookies=self.cookies_dict)
    def detail(self, response):
        spu_name = response.meta.get('spu_name')
        data = response.text
        index = data.find('(')
        data_str = data[index + 1:-1]
        data_dict = json.loads(data_str)
        res = data_dict.get('data').get('result')
        # 详情信息
        detailInfo = res.get('detailInfo')
        desc = detailInfo.get('desc')
        desc = desc.replace(' ', '')
        detailImage = detailInfo.get("detailImage")[0].get('list')
        # 商品信息
        skuInfo = res.get('skuInfo')
        default_image = skuInfo.get('img')
        sku_title = skuInfo.get('title')
        sku_info = {}
        spu_specs = {}
        spu_specs_list = []
        # 颜色、尺码
        spu_id = None
        if skuInfo.get('props'):
            for prop in skuInfo.get('props'):
                spu_spec_name = prop.get('label')
                spu_specs_list.append(spu_spec_name)
                # -------------------------------spu查询
                msg = Spu().select(spu_name)
                if msg:
                    if msg[0]:
                        spu_id = msg[0]
                        category2_id = msg[1]
                        # -------------------------------spuspecification表
                        SpuSpecs().insert(spu_spec_name, spu_id)
        for i in detailImage:
            desc_image = FastFdfs().upload(i)
            # ---------------------------------DetailImag表
            DetailImag().insert(desc, desc_image, spu_id)
        for sku in skuInfo.get('skus'):
            price = float(sku.get('price') / 100)
            nowprice = float(sku.get('nowprice') / 100)
            img = sku.get('img')
            style = sku.get('style')
            size = sku.get('size')
            stock = sku.get('stock')
            if skuInfo.get('props'):
                if len(skuInfo.get('props')) == 1:
                    if style:
                        spu_specs[spu_specs_list[0]] = style
                    if size:
                        spu_specs[spu_specs_list[0]] = size
                        # ----------------spuspecs查询
                    msg = SpuSpecs().select(spu_specs_list[0], spu_id)
                    if msg:
                        if msg[0]:
                            spec_id = msg[0]
                            # --------------SpecsOption表
                            SpecsOption().insert(spu_specs[spu_specs_list[0]],
                                                 spec_id)
                            # ---------------------------------SpecsOption查询
                            m = SpecsOption().select(spu_specs[spu_specs_list[0]],
                                                     spec_id)
                            if m:
                                if m[0]:
                                    option_id = m[0]
                else:
                    if style:
                        spu_specs[spu_specs_list[0]] = style
                        # ----------------spuspecs查询
                        msg = SpuSpecs().select(spu_specs_list[0], spu_id)
                        if msg:
                            if msg[0]:
                                spec_id = msg[0]
                                # ---------SpecsOption表
                                SpecsOption().insert(spu_specs[spu_specs_list[0]], spec_id)
                                # ---------------------------------SpecsOption查询
                                m = SpecsOption().select(spu_specs[spu_specs_list[0]],
                                                         spec_id)
                                if m:
                                    if m[0]:
                                        option_id = m[0]
                    if size:
                        spu_specs[spu_specs_list[1]] = size
                        # ----------------spuspecs查询
                        msg = SpuSpecs().select(spu_specs_list[1], spu_id)
                        if msg:
                            if msg[0]:
                                spec_id = msg[0]
                                # ---------SpecsOption表
                                SpecsOption().insert(spu_specs[spu_specs_list[1]], spec_id)
                                # ---------------------------------SpecsOption查询
                                m = SpecsOption().select(spu_specs[spu_specs_list[1]],
                                                         spec_id)
                                if m:
                                    if m[0]:
                                        option_id = m[0]
            default_image_url = FastFdfs().upload(default_image)
            # -------------------sku表
            sku_id = Sku().insert(sku_title, price, nowprice, stock, default_image_url, category2_id,
                                  spu_id)
            # ---------------------------------SkuSpecification表
            SkuSpecification().insert(option_id, sku_id, spec_id)
            img_url = FastFdfs().upload(img)
            # ---------------------------------SkuImag表
            SkuImag().insert(img_url, sku_id)
