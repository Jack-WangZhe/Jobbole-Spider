# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import datetime
import scrapy
import re
from scrapy.loader.processors import MapCompose,TakeFirst,Join
from scrapy.loader import ItemLoader

class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

#处理的函数,value表示input的值,即初始值
def add_jobbole(value):
    return value+"-jobbole"

#处理时间函数
def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date

#获得字符串中数字
def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums

#去掉含有评论的tag
def remove_comment_tags(value):
    if "评论" in value:
        return ""
    else:
        return value

#什么都不做的函数,专门用于覆盖default_output_processor
def return_value(value):
    return value

class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field(
        input_processor = MapCompose(add_jobbole) #Mapcompose表示可以对传入的内容调用多个函数进行预处理
    ) #scrapy可以使用Field表示任意类型
    create_date = scrapy.Field(
        input_processor = MapCompose(date_convert),
        output_processor = TakeFirst() #使用TakeFirst函数可以只获得数组中的第一个
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field() #对url进行编码
    front_image_url = scrapy.Field(
        output_processor = MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor  =MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags), #tags中可能包含评论数,则需要定义一个函数去掉含评论的tag
        output_processor=Join(",") #使用Join函数连接数组中的内容,使用output_processor可以覆盖掉default_output_processor
    )
    content = scrapy.Field()

#自定义itemloader
class ArticleItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()