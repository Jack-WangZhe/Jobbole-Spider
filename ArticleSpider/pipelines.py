# -*- coding: utf-8 -*-
#利用codecs打开文件
import codecs
import json
import MySQLdb
import MySQLdb.cursors
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi

class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item

# 将结果存储成json
class JsonWithEncodingPipeline(object):
    def __init__(self):
        # 利用codecs方式打开文件,与open函数不同在于编码,可以省去很多编码方面的繁杂工作
        self.file =  codecs.open("article.json","w",encoding="utf-8")
    def process_item(self, item, spider):
        #利用json.dumps函数将item存储成json
        lines = json.dumps(dict(item),ensure_ascii=False) + "\n"
        #写入json文件中
        self.file.write(lines)
        #process_item函数一定要返回item,因为下一个pipeline还会使用此item
        return item
    #在spider close的时候关闭file
    def spider_closed(self,spider):
        self.file.close()

# 利用json exporter
class JsonExporterPipeline(object):
    #调用scrapy提供的json exporter导出json文件
    def __init__(self):
        self.file = open('articleexporter.json','wb') # 二进制方式打开
        self.exporter = JsonItemExporter(self.file,encoding = "utf-8",ensure_ascii=False)
        self.exporter.start_exporting()
    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
    def close_spider(self,spider):
        self.exporter.finish_exporting()
        self.file.close()

# 继承ImagePipeline
class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            # result中包含一个tuple,一个是状态值,一个是返回对象
            for ok,value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path
        return item

#Mysql pipeline
class MysqlPipeline(object):
    def __init__(self):
        #连接mysqldb,创建连接
        self.conn = MySQLdb.connect('127.0.0.1','root','123456','scrapy',charset="utf8",use_unicode=True)
        #创建cursor
        self.cursor = self.conn.cursor()
    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article(title,create_date,url,url_object_id,front_image_url,front_image_path,comment_nums,fav_nums,praise_nums,tags,content)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        self.cursor.execute(insert_sql,(item["title"],item["create_date"],item["url"],item["url_object_id"],item["front_image_url"],item["front_image_path"],item["comment_nums"],item["fav_nums"],item["praise_nums"],item["tags"],item["content"]))
        self.conn.commit()

#异步mysql插入
class MysqlTwistedPipeline(object):
    #setting中包含setting.py中的内容
    @classmethod
    def from_settings(cls,settings):
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            charset = "utf8",
            cursorclass = MySQLdb.cursors.DictQursor,
            use_unicode = True
        )
        #创建连接池,参数1使用的dbapi的name,
        dbpool = adbapi.ConnectionPool("MySQLdb",**dbparms)
        return cls(dbpool)
    def __init__(self,dbpool):
        self.dbpool = dbpool
    def process_item(self, item, spider):
        #使用twisted将mysql插入变成异步执行,参数1表示要异步执行的函数,参数2表示执行的item
        query= self.dbpool.runInteraction(self.do_insert,item)
        query.addErrback(self.handle_error)#处理异常
    def do_insert(self,cursor,item):
        #执行具体的插入
        insert_sql = """
                    insert into jobbole_article(title,create_date,url,url_object_id,front_image_url,front_image_path,comment_nums,fav_nums,praise_nums,tags,content)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """
        cursor.execute(insert_sql, (
        item["title"], item["create_date"], item["url"], item["url_object_id"], item["front_image_url"],
        item["front_image_path"], item["comment_nums"], item["fav_nums"], item["praise_nums"], item["tags"],
        item["content"]))
        #不需要commit,会自动进行commit
    def handle_error(self,failure):
        #处理异步插入的异常
        print(failure)