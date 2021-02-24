import datetime
import re,requests,pymysql

from fdfs_client.client import Fdfs_client

client = Fdfs_client('/home/time/malls/Time_mall/Time_mall/GoodsData/fastfdfs/client.conf')
class FastFdfs:
    def upload(self,file):
        global client
        img_byte = requests.get(file).content
        res = client.upload_by_buffer(img_byte, file_ext_name='png')
        if res.get('Status') == 'Upload successed.':
            img = res.get('Remote file_id')
            img = 'http://192.168.2.33:8888/' + img.replace('\\', '/')
            return img
        return None
    def download(self):
        pass
class ProductId:
    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1',port=3306, user='Time',password='liujun',db='Time_mall',charset='utf8')
        self.cur = self.conn.cursor()

    def insert(self,pid):
        create_time = datetime.datetime.today()
        update_time = datetime.datetime.today()
        print('tb_product_id',pid)
        msg = self.select(pid)
        if not msg:
            sql = "insert into tb_product_id(pid,create_time,update_time) values('{}','{}','{}');".format(pid,create_time,update_time)
            try:
                self.cur.execute(sql)
                self.conn.commit()
            except Exception as e:
                print(e)
                self.conn.rollback()
    def select(self,pid):
        sql = "select id from tb_product_id where pid='%s';" % pid
        self.cur.execute(sql)
        self.conn.commit()
        msg = self.cur.fetchone()
        return msg
    def __del__(self):
        self.cur.close()
        self.conn.close()
class GoodsCategory:
    def __init__(self):
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
        print('tb_spu_specification', name, spu_id)
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
        print('tb_specification_option', name, spec_id)
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

    def insert(self, name, price,now_price,stock,default_image,category_id,spu_id):
        print('tb_sku', name, price,now_price,stock,default_image,category_id,spu_id)
        create_time = datetime.datetime.today()
        update_time = datetime.datetime.today()
        global count
        count +=1
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
        print('tb_sku_image', image,sku_id)
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
        print('tb_desc_image', desc,desc_image,spu_id)
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
        print('tb_sku_specification', option_id,sku_id,spec_id)
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
