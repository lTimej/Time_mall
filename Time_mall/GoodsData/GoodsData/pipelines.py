import datetime
import re,requests,pymysql

from fdfs_client.client import Fdfs_client

client = Fdfs_client('/home/time/malls/Time_mall/Time_mall/GoodsData/fastfdfs/client.conf')
class FastFdfs:
    '''
    #FastDFS上传和下载
    '''
    def upload(self,file):#上传
        global client#全局变量
        #下载二进制照片
        img_byte = requests.get(file).content
        #上传到服务器，返回路径
        res = client.upload_by_buffer(img_byte, file_ext_name='png')
        if res.get('Status') == 'Upload successed.':
            img = res.get('Remote file_id')
            img = img.replace('\\', '/')
            return img
        return None
    def download(self):#下载
        pass
class ProductId:
    def __init__(self):
        #链接数据库
        self.conn = pymysql.connect(host='127.0.0.1',port=3306, user='Time',password='liujun',db='Time_mall',charset='utf8')
        #
        self.cur = self.conn.cursor()

    def insert(self,pid):
        '''
        商品类别
        :param pid:
        :return:
        '''
        print('tb_product_id',pid)
        create_time = datetime.datetime.today()
        update_time = datetime.datetime.today()
        msg = self.select(pid)
        #不存在则保存数据
        if not msg:
            sql = "insert into tb_product_id(pid,create_time,update_time) values('{}','{}','{}');".format(pid,create_time,update_time)
            try:
                self.cur.execute(sql)
                self.conn.commit()
            except Exception as e:
                print(e)#出错进行回滚操作
                self.conn.rollback()
    def select(self,pid):
        '''
        查找
        :param pid:
        :return:
        '''
        #查找id
        sql = "select id from tb_product_id where pid='%s';" % pid
        self.cur.execute(sql)
        self.conn.commit()
        #返回元祖
        msg = self.cur.fetchone()
        return msg
    def __del__(self):
        #执行完就关闭
        self.cur.close()
        self.conn.close()
class GoodsCategory:
    def __init__(self):
        '''
        商品分类数据库的插入和删除
        '''
        self.conn = pymysql.connect(host='127.0.0.1',port=3306, user='Time',password='liujun',db='Time_mall',charset='utf8')
        self.cur = self.conn.cursor()
    def insert(self,title,parent_id=None):
        print('tb_goods_category',title,parent_id)
        create_time = datetime.datetime.today()
        update_time = datetime.datetime.today()
        if parent_id:
            sql = "insert into tb_goods_category(name,parent_id,create_time,update_time) values('{}','{}','{}','{}');".format(title,parent_id,create_time,update_time)
        else:
            sql = "insert into tb_goods_category(name,create_time,update_time) values('{}','{}','{}');" .format(title,create_time,update_time)
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()
    def select(self,title=None,category_id=None):
        if not category_id:
            sql = "select id,parent_id from tb_goods_category where name='%s';" % title
        else:
            sql = "select parent_id from tb_goods_category where id='%d';" % category_id
        self.cur.execute(sql)
        self.conn.commit()
        msg = self.cur.fetchmany()
        return msg
    def __del__(self):
        self.cur.close()
        self.conn.close()
class GoodsList:
    def __init__(self):
        '''
        商品列表的插入和查找
        '''
        self.conn = pymysql.connect(host='127.0.0.1',port=3306, user='Time',password='liujun',db='Time_mall',charset='utf8')
        self.cur = self.conn.cursor()
    def insert(self,url,sequeue,category_id,pid_id):
        print('tb_goods_list',url,sequeue,category_id,pid_id)
        create_time = datetime.datetime.today()
        update_time = datetime.datetime.today()
        sql = "insert into tb_goods_list(url,sequeue,category_id,pid_id,create_time,update_time) values('{}','{}','{}','{}','{}','{}');".format(url,sequeue,category_id,pid_id,create_time,update_time)
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()
    def select(self,category_id):
        sql = "select id from tb_goods_list where category_id='%d';" % category_id
        self.cur.execute(sql)
        self.conn.commit()
        msg = self.cur.fetchone()
        return msg
    def __del__(self):
        self.cur.close()
        self.conn.close()
class Spu:
    def __init__(self):
        '''
        spu的插入和查找
        '''
        self.conn = pymysql.connect(host='127.0.0.1',port=3306, user='Time',password='liujun',db='Time_mall',charset='utf8')
        self.cur = self.conn.cursor()
    def insert(self,name,category1_id,category2_id):
        print('tb_spu',name,category1_id,category2_id)
        create_time = datetime.datetime.today()
        update_time = datetime.datetime.today()
        sql = "insert into tb_spu(name,category1_id,category2_id,sales,cfavs,create_time,update_time) values('{}','{}','{}','{}','{}','{}','{}');".format(name,category1_id,category2_id,0,0,create_time,update_time)
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()
    def select(self,name):
        sql = "select id,category2_id from tb_spu where name='%s';" % name
        self.cur.execute(sql)
        self.conn.commit()
        msg = self.cur.fetchone()
        return msg
    def __del__(self):
        self.cur.close()
        self.conn.close()
class SpuSpecs:
    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1',port=3306, user='Time',password='liujun',db='Time_mall',charset='utf8')
        self.cur = self.conn.cursor()

    def insert(self, name, spu_id):
        print('tb_spu_specs',name,spu_id)
        create_time = datetime.datetime.today()
        update_time = datetime.datetime.today()
        sql = "insert into tb_spu_specification(name,spu_id,create_time,update_time) values('{}','{}','{}','{}');".format(name,spu_id,create_time,update_time)
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()

    def select(self, name,spu_id=None):
        if not spu_id:
            sql = "select id from tb_spu_specification where name='%s';" % name
        else:
            sql = "select id from tb_spu_specification where name='%s' and spu_id='%d';" % (name,spu_id)
        self.cur.execute(sql)
        self.conn.commit()
        msg = self.cur.fetchone()
        return msg

    def __del__(self):
        self.cur.close()
        self.conn.close()
class SpecsOption:
    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1', port=3306, user='Time', password='liujun', db='Time_mall',charset='utf8')
        self.cur = self.conn.cursor()

    def insert(self, name, spec_id):
        print('tb_spec_option',name,spec_id)
        create_time = datetime.datetime.today()
        update_time = datetime.datetime.today()
        sql = "insert into tb_specification_option(value,spec_id,create_time,update_time) values('{}','{}','{}','{}');".format(name,spec_id,create_time,update_time)
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()

    def select(self, value,spec_id):
        sql = "select id from tb_specification_option where value='%s' and spec_id='%d';" % (value,spec_id)
        self.cur.execute(sql)
        self.conn.commit()
        msg = self.cur.fetchone()
        return msg

    def __del__(self):
        self.cur.close()
        self.conn.close()
count = 0
class Sku:
    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1',port=3306, user='Time',password='liujun',db='Time_mall',charset='utf8')
        self.cur = self.conn.cursor()

    def insert(self, name, price,now_price,stock,category_id,spu_id,default_image=None):
        print('tb_sku',name,price,now_price,default_image,category_id,spu_id)
        create_time = datetime.datetime.today()
        update_time = datetime.datetime.today()
        global count
        count +=1
        # if not default_image:
        #     return count
        sql = "insert into tb_sku(title,price,now_price,stock,default_image,category_id,spu_id,sales,comments,is_launched,create_time,update_time) values('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}');".format(name,price,now_price,stock,default_image,category_id,spu_id,0,0,1,create_time,update_time)
        try:
            self.cur.execute(sql)
            self.conn.commit()
            return count
        except Exception as e:
            print(e)
            self.conn.rollback()

    def select(self, name):
        sql = "select id from tb_sku where title='%s';" % name
        self.cur.execute(sql)
        self.conn.commit()
        msg = self.cur.fetchone()
        return msg
    def counter(self):
        n = 1
        return n+1
    def __del__(self):
        self.cur.close()
        self.conn.close()
class SkuImag:
    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1', port=3306, user='Time', password='liujun', db='Time_mall',charset='utf8')
        self.cur = self.conn.cursor()
    def insert(self, image,sku_id):
        print('tb_sku_image',image,sku_id)
        create_time = datetime.datetime.today()
        update_time = datetime.datetime.today()
        sql = "insert into tb_sku_image(image,sku_id,create_time,update_time) values('{}','{}','{}','{}');".format(image,sku_id,create_time,update_time)
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()
    def select(self, image):
        sql = "select id from tb_sku_image where image='%s';" % image
        self.cur.execute(sql)
        self.conn.commit()
        msg = self.cur.fetchone()
        return msg
    def __del__(self):
        self.cur.close()
        self.conn.close()
class DetailImag:
    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1',port=3306, user='Time',password='liujun',db='Time_mall',charset='utf8')
        self.cur = self.conn.cursor()
    def insert(self, desc,desc_image,spu_id):
        print('tb_detail_image',desc,desc_image,spu_id)
        create_time = datetime.datetime.today()
        update_time = datetime.datetime.today()
        sql = "insert into tb_spu_desc(detail_info,desc_image,spu_id,create_time,update_time) values('{}','{}','{}','{}','{}');".format(desc,desc_image,spu_id,create_time,update_time)
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()
    def select(self, desc_image):
        sql = "select id from tb_spu_desc where desc_image='%s';" % desc_image
        self.cur.execute(sql)
        self.conn.commit()
        msg = self.cur.fetchone()
        return msg
    def __del__(self):
        self.cur.close()
        self.conn.close()
class SkuSpecification:
    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1',port=3306, user='Time',password='liujun',db='Time_mall',charset='utf8')
        self.cur = self.conn.cursor()

    def insert(self, option_id,sku_id,spec_id):
        print('tb_sku_spec',option_id,sku_id,spec_id)
        create_time = datetime.datetime.today()
        update_time = datetime.datetime.today()
        sql = "insert into tb_sku_specification(option_id,sku_id,spec_id,create_time,update_time) values('{}','{}','{}','{}','{}');".format(option_id,sku_id,spec_id,create_time,update_time)
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()

    def select(self, sku_id):
        sql = "select id from tb_sku_specification where sku_id='%sd';" % sku_id
        self.cur.execute(sql)
        self.conn.commit()
        msg = self.cur.fetchone()
        return msg

    def __del__(self):
        self.cur.close()
        self.conn.close()
class AdCategory:
    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1',port=3306, user='Time',password='liujun',db='Time_mall',charset='utf8')
        self.cur = self.conn.cursor()

    def insert(self, title):
        print('tb_adcategory',title)
        create_time = datetime.datetime.today()
        update_time = datetime.datetime.today()
        sql = "insert into tb_ad_category(create_time,update_time,title) values('{}','{}','{}');".format(create_time,update_time,title)
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()

    def select(self, name):
        sql = "select id from tb_ad_category where title='%s';" % name
        self.cur.execute(sql)
        self.conn.commit()
        msg = self.cur.fetchone()
        return msg
    def __del__(self):
        self.cur.close()
        self.conn.close()
class ContentCategory:
    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1',port=3306, user='Time',password='liujun',db='Time_mall',charset='utf8')
        self.cur = self.conn.cursor()

    def insert(self, title,cid,adCategory_id):
        print('tb_content_category',title,cid,adCategory_id)
        create_time = datetime.datetime.today()
        update_time = datetime.datetime.today()
        sql = "insert into tb_content_category(create_time,update_time,title,cid,adCategory_id) values('{}','{}','{}','{}','{}');".format(create_time,update_time,title,cid,adCategory_id)

        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()

    def select(self, cid):
        sql = "select id from tb_content_category where cid='%s';" % cid
        self.cur.execute(sql)
        self.conn.commit()
        msg = self.cur.fetchone()
        return msg
    def __del__(self):
        self.cur.close()
        self.conn.close()
class Content:
    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1',port=3306, user='Time',password='liujun',db='Time_mall',charset='utf8')
        self.cur = self.conn.cursor()

    def insert(self, title,url,image,sequence,status,category_id,price=None,discountprice=None):
        print('tb_content',title,url,image,sequence,category_id,price,discountprice)
        create_time = datetime.datetime.today()
        update_time = datetime.datetime.today()
        if image:
            image = FastFdfs().upload(image)
        if not image:
            sql = "insert into tb_content(create_time,update_time,title,url,sequence,status,category_id,price) values('{}','{}','{}','{}','{}','{}','{}');".format(
                create_time, update_time, title, url, sequence,status,category_id)
        if price and discountprice:
            sql = "insert into tb_content(create_time,update_time,title,url,image,sequence,status,category_id,price,discountprice) values('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}');".format(create_time,update_time,title,url,image,sequence,status,category_id,price,discountprice)
        elif price and not discountprice:
            sql = "insert into tb_content(create_time,update_time,title,url,image,sequence,status,category_id,price) values('{}','{}','{}','{}','{}','{}','{}','{}','{}');".format(
                create_time, update_time, title, url, image, sequence,status,category_id, price)
        else:
            sql = "insert into tb_content(create_time,update_time,title,url,image,sequence,status,category_id) values('{}','{}','{}','{}','{}','{}','{}','{}');".format(create_time,update_time,title,url,image,sequence,status,category_id)
        try:
            self.cur.execute(sql)
            self.conn.commit()
            return
        except Exception as e:
            print(e)
            self.conn.rollback()

    def select(self, name):
        sql = "select id from tb_content where title='%s';" % name
        self.cur.execute(sql)
        self.conn.commit()
        msg = self.cur.fetchone()
        return msg
    def __del__(self):
        self.cur.close()
        self.conn.close()
