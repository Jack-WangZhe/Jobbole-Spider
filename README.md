## Python爬虫爬取伯乐在线

### 一.环境搭建

#### 1.创建环境

* 执行`pip install scrapy`安装scrapy
* 使用`scrapy startproject ArticleSpider`创建scrapy项目
* 使用pycharm导入创建的scrapy项目

#### 2.项目结构

* scrapy.cfg：scrapy配置文件
* settings.py：配置代码文件信息
* pipelines.py：和数据存储相关的文件
* middlewares.py：存放中间件
* items.py：定义数据保存的格式
* spiders文件夹存放爬虫文件

#### 3.使用命令创建爬虫文件

* `scrapy genspider 爬虫名称 网站域名`在spiders文件夹中创建爬虫文件

### 二.xpath编写爬虫代码

#### 1.编写设计

* pycharm没有scrapy模板，所以没法调试，我们可以通过创建`main.py`文件调用命令行，完成调试。

* 在项目外侧创建main.py，代码如下

  ```python
  #execute函数可以执行scrapy脚本
  from scrapy.cmdline import execute
  #需要sys获得工程目录
  import sys
  #利用os获得工程目录
  import os
  #需要设置工程目录,设置完工程目录之后调用execute函数才会生效
  #print(os.path.dirname(os.path.abspath(__file__)))则会获取到当前main文件的路径的上一级包名
  sys.path.append(os.path.dirname(os.path.abspath(__file__)))
  #execute相当于执行命令
  execute(["scrapy","crawl","jobbole"])
  ```

* 【注意】：设置setting中的`ROBOTSTXT_OBEY=False`，如果不设置scrapy会默认读取每一个网站上的robots协议，会把不符合协议的url给过滤掉，很快就会执行结束

* 执行debug main则会以debug模式运行爬虫

#### 2.利用xpath提取值

* xpath简介

  * xpath使用路径表达式在xml和html中进行导航
  * xpath包括标准函数库
  * xpath是一个w3c的标准

* xpath节点关系

  * 父节点
  * 子节点
  * 同胞节点
  * 先辈节点
  * 后代节点

* xpath语法

  | 表达式       | 说明                                                         |
  | ------------ | ------------------------------------------------------------ |
  | article      | 选取所有article元素的所有子节点                              |
  | /article     | 选取根元素article                                            |
  | article/a    | 选取所有属于article的子元素的a元素                           |
  | //div        | 选取所有div子元素（不论出现在文档的任何地方）                |
  | article//div | 选取所有属于article元素的后代的div元素，不管它出现在article之下的任何位置 |
  | //@class     | 选取所有名为class的属性                                      |

* xpath语法-谓语

  | 表达式                 | 说明                                     |
  | ---------------------- | ---------------------------------------- |
  | /article/div[1]        | 选取属于article子元素的第一个div元素     |
  | /article/div[last()]   | 选取属于article子元素的最后一个div元素   |
  | /article/div[last()-1] | 选取属于article子元素的倒数第二个div元素 |
  | //div[@lang]           | 选取所有拥有lang属性的div元素            |
  | //div[@lang='eng']     | 选取所有lang属性为eng的div元素           |

* xpath其他语法

  | 表达式                  | 说明                                                         |
  | ----------------------- | ------------------------------------------------------------ |
  | /div/*                  | 选取属于div元素的所有子节点                                  |
  | //*                     | 选取所有元素                                                 |
  | //div[@*]               | 选取所有带属性的div元素                                      |
  | //div/a \| //div/p      | 选取所有div元素的a和p元素                                    |
  | //span \| //ul          | 选取文档中的span和ul元素                                     |
  | article/div/p \| //span | 选取所有属于article元素和div元素的p元素 以及文档中所有span元素 |

  * 如果想通过属性取值则需要给定标签元素的内容，如果是任意标签则给定*
  * 如果通过`@class="class类"`取值，则只会匹配class只有指定的元素；如果想指定包含指定class的元素则需要使用函数`contains(@class,"class类")`

* xpath使用

  * **[注意]:页面上的查看源码跟检查控制台的element不一定一样，源码是源代码的html文件，检查控制台的element会有js动态生成的dom**

  * jobbole.py

    ```python
    # -*- coding: utf-8 -*-
    import scrapy
    
    class JobboleSpider(scrapy.Spider):
        name = 'jobbole'
        allowed_domains = ['blog.jobbole.com']
        start_urls = ['http://blog.jobbole.com/114610/'] #放入想爬取的所有url
    
        def parse(self, response):
            #/html/body/div[3]/div[3]/div[1]/div[1]
            #//*[@id="post-114610"]/div[1]/h1
            #scrapy返回的是一个selector而不是node,是为了方便进一步获取selector下面的selector
            re_selector = response.xpath('//*[@id="post-114610"]/div[1]/h1')
            re2_selector = response.xpath('//*[@id="post-114610"]/div[1]/h1/text()') #利用text()函数获取元素中的值
            pass
    ```

* 如果每一次调试都运行python脚本发送http请求获取内容效率低，可以通过`scrapy shell url路径`的方式通过shell进行调试

  ```python
  #以下是在命令行输入
  scrapy shell http://blog.jobbole.com/114610/
  re_selector = response.xpath('//*[@id="post-114610"]/div[1]/h1')
  re_selector.extract()#提取selector的内容['<h1>微软变了！招程序员的流程完全改了</h1>']
  re_selector.extract()[0]#获得列表中的第一个元素 '<h1>微软变了！招程序员的流程完全改了</h1>'
  #如果提取的字符串左右有回车符换行符等等,则需要使用strip()将其去掉
  #re_selector.extract()[0].strip()
  ```

* 使用xpath爬取伯乐在线网站内容[jobbole.py]

  ```python
  # -*- coding: utf-8 -*-
  import scrapy
  import re
  
  class JobboleSpider(scrapy.Spider):
      name = 'jobbole'
      allowed_domains = ['blog.jobbole.com']
      start_urls = ['http://blog.jobbole.com/114610/'] #放入想爬取的所有url
  
      def parse(self, response):
          # 获取文章title
          title = response.xpath('//*[@id="post-114610"]/div[1]/h1/text()')
          # 获取文章创建时间
          create_date = response.xpath('//*[@id="post-114610"]/div[2]/p/text()').extract()[0].strip().replace("·","").strip()
          # 通过contains函数选择class中包含vote-post-up的元素，获得点赞数
          praise = response.xpath('//*[contains(@class,"vote-post-up")]/h10/text()').extract()[0]
          # 收藏数,获取的是字符串,需要使用正则表达式取出
          collect = response.xpath('//*[contains(@class,"bookmark-btn")]/text()').extract()[0]
          match_re = re.match(".*?(\d+).*",collect)
          if match_re:
              collect = match_re.group(1)
          else:
              collect = 0
          # 评论数
          comment = response.xpath('//a[@href="#article-comment"]/span/text()').extract()[0]
          match_re = re.match(".*?(\d+).*", comment)
          if match_re:
              comment = match_re.group(1)
          else:
              comment = 0
          # 文章内容
          content = response.xpath('//div[@class="entry"]').extract()[0]
          # 文章标签
          tag = response.xpath('//*[@id="post-114610"]/div[2]/p/a/text()').extract()
          # 利用列表生成式过滤携带评论的文章标签
          tag = [element for element in tag if not element.strip().endswith("评论")]
          # 利用join方式将列表拼成一个字符串
          tags = ",".join(tag)
          pass
  ```

### 三.css选择器编写爬虫代码

#### 1.css选择器语法

| 表达式                       | 说明                                   |
| ---------------------------- | -------------------------------------- |
| *                            | 选择所有节点                           |
| #container                   | 选择id为container的节点                |
| .container                   | 选取所有class包含container的节点       |
| li a                         | 选取所有li下的所有a节点                |
| ul + p                       | 选择ul后面的第一个p元素                |
| div#container>ul             | 选取id为container的第一个ul子元素      |
| ul ~ p                       | 选取与ul相邻的所有p元素                |
| a[title]                     | 选取所有有title属性的a元素             |
| a[href="http://jobbole.com"] | 选取所有href属性为jobbole.com值的a元素 |
| a[href*="jobble"]            | 选取所有href属性包含jobbole的a元素     |
| a[href^="http"]              | 选取所有href属性以http开头的a元素      |
| a[href$=".jpg"]              | 选取所有href属性以jpg结尾的a元素       |
| input[type=radio]:checked    | 选择选中的radio元素                    |
| div:not(#container)          | 选取所有id非container的div属性         |
| li:nth-child(3)              | 选取第三个li元素                       |
| tr:nth-child(2n)             | 第偶数个tr                             |
| ::text                       | 利用伪类选择器获得选中的元素的内容     |

#### 2.利用css选择器提取值

* 使用`response.css("选择器内容")`通过css选择器获得内容

* 利用css选择器提取伯乐在线平台内容[jobbole.py]

  ```python
  # -*- coding: utf-8 -*-
  import scrapy
  import re
  
  class JobboleSpider(scrapy.Spider):
      name = 'jobbole'
      allowed_domains = ['blog.jobbole.com']
      start_urls = ['http://blog.jobbole.com/114610/'] #放入想爬取的所有url
  
      def parse(self, response):
          ######################
          ## 利用css选择器获取内容
          ######################
          title = response.css(".entry-header h1::text").extract()[0]
          create_date = response.css("p.entry-meta-hide-on-mobile::text").extract()[0].strip().replace("·", "").strip()
          # 点赞数
          praise_nums = response.css(".vote-post-up h10::text").extract()[0]
          # 收藏数
          collect = response.css('span.bookmark-btn::text').extract()[0]
          match_re = re.match(".*?(\d+).*", collect)
          if match_re:
              collect = match_re.group(1)
          # 评论数
          comment = response.css('a[href="#article-comment"] span::text').extract()[0]
          match_re = re.match(".*?(\d+).*", comment)
          if match_re:
              comment = match_re.group(1)
          # 获得文章内容
          content = response.css("div.entry").extract()[0]
          # 获得标签
          tags = response.css("p.entry-meta-hide-on-mobile a::text").extract()
          tag = [element for element in tags if not element.strip().endswith("评论")]
          tags = ",".join(tag)
          pass
  ```

* **如果想使用extract将selector变成list后取得第一个除了使用`extract()[0]`之后还可以使用`extract_first()`，如果获取的是空的话，使用`extract()[0]`会报错，而`extract_first()`不会报错，还可以在参数设定默认值，如果没有值则返回对应的内容**

### 四.真实爬取数据

#### 1.获取文章列表页中的文章url并交给scrapy下载后并进行解析

#### 2.获取下一页url并交给scrapy进行下载，下载完成后交给parse

* 实例代码[jobbole.py]

  ```python
  # -*- coding: utf-8 -*-
  import scrapy
  import re
  from scrapy.http import Request
  from urllib import parse
  
  class JobboleSpider(scrapy.Spider):
      name = 'jobbole'
      allowed_domains = ['blog.jobbole.com']
      start_urls = ['http://blog.jobbole.com/all-posts/'] #放入想爬取的所有url
  
      def parse(self, response):
          """
          1.获取文章列表页中的文章url并交给scrapy下载后并进行解析
          2.获取下一页url并交给scrapy进行下载，下载完成后交给parse
          :param response:
          :return:
          """
  
          #解析列表页的所有文章url并交给scrapy下载后进行解析
          #利用::attr()伪类选择器获得对应元素的属性值
          post_urls = response.css("#archive .floated-thumb .post-thumb a::attr(href)").extract()
          for post_url in post_urls:
              #利用Request方法提交请求获取对应url内容
              #url表示访问的url(parse.urljoin是借助urllib将当前url与请求url进行拼接,从而获取到真实的url),callback表示回调的函数
              yield Request(url=parse.urljoin(response.url,post_url),callback=self.parse_detail)
  
          #提交下一页并交给scrapy进行下载
          #两个类之间有空格则表示子元素,两个类中间没空格则表示同时满足两个类的元素
          next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
          if next_url:
              yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)
  
      #提取文章的具体字段
      def parse_detail(self,response):
          ######################
          ## 利用css选择器获取内容
          ######################
          title = response.css(".entry-header h1::text").extract()[0]
          print(title)
          create_date = response.css("p.entry-meta-hide-on-mobile::text").extract()[0].strip().replace("·", "").strip()
          # 点赞数
          praise_nums = response.css(".vote-post-up h10::text").extract()[0]
          # 收藏数
          collect = response.css('span.bookmark-btn::text').extract()[0]
          match_re = re.match(".*?(\d+).*", collect)
          if match_re:
              collect = match_re.group(1)
          else:
              collect = 0
          # 评论数
          comment = response.css('a[href="#article-comment"] span::text').extract()[0]
          match_re = re.match(".*?(\d+).*", comment)
          if match_re:
              comment = match_re.group(1)
          else:
              comment = 0
          # 获得文章内容
          content = response.css("div.entry").extract()[0]
          # 获得标签
          tags = response.css("p.entry-meta-hide-on-mobile a::text").extract()
          tag = [element for element in tags if not element.strip().endswith("评论")]
          tags = ",".join(tag)
  ```

* 开发流程

  * 利用Request函数执行访问指定url并通过callback回调函数处理进入url后的操作
  * 利用parse.urljoin自动将对应url添加域名，参数1是域名，参数2是url
  * 利用yield实现异步请求
  * 利用`::attr()`伪类选择器获取对应属性的值

### 五.数据存储

> 数据爬取的目的在于将非结构的数据源提取成结构型的数据
>
> 如果想使用Request函数向callback函数中传递内容,则需要使用meta参数

#### 1.使用meta向Request函数的callback中传递内容

* 需求说明：在列表页获取图片url连接传递到parse_detail函数进行解析

* 实现思路

  * 获取时需要将之前直接获取a下的href变成先获取node节点，之后获得a下的img的src，再获取a的href，在使用Request函数中添加meta参数内容放上img_url传递给callback函数中的response
  * 在response中获取之前存入的img_url，使用`response.meta.get("front_image_url","")`

* 实例代码

  ```python
  # -*- coding: utf-8 -*-
  import scrapy
  import re
  from scrapy.http import Request
  from urllib import parse
  
  class JobboleSpider(scrapy.Spider):
      name = 'jobbole'
      allowed_domains = ['blog.jobbole.com']
      start_urls = ['http://blog.jobbole.com/all-posts/'] #放入想爬取的所有url
  
      def parse(self, response):
          """
          1.获取文章列表页中的文章url并交给scrapy下载后并进行解析
          2.获取下一页url并交给scrapy进行下载，下载完成后交给parse
          :param response:
          :return:
          """
  
          #解析列表页的所有文章url并交给scrapy下载后进行解析
          #利用::attr()伪类选择器获得对应元素的属性值
          post_nodes = response.css("#archive .floated-thumb .post-thumb a")
          for post_node in post_nodes:
              image_url = post_node.css("img::attr(src)").extract_first("") #获得图片的src
              post_url = post_node.css("::attr(href)").extract_first("") #获得连接的href
              #利用Request方法提交请求获取对应url内容
              #url表示访问的url(parse.urljoin是借助urllib将当前url与请求url进行拼接,从而获取到真实的url),callback表示回调的函数
              yield Request(url=parse.urljoin(response.url,post_url),meta={"front_image_url":image_url},callback=self.parse_detail)
  
          #提交下一页并交给scrapy进行下载
          #两个类之间有空格则表示子元素,两个类中间没空格则表示同时满足两个类的元素
          next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
          if next_url:
              yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)
  
      #提取文章的具体字段
      def parse_detail(self,response):
          ######################
          ## 利用css选择器获取内容
          ######################
          # 获得meta中的front_image_url,文章封面图
          front_image_url = response.meta.get("front_image_url","")
          # 获得title 
          title = response.css(".entry-header h1::text").extract()[0]
          print(title)
          create_date = response.css("p.entry-meta-hide-on-mobile::text").extract()[0].strip().replace("·", "").strip()
          # 点赞数
          praise_nums = response.css(".vote-post-up h10::text").extract()[0]
          # 收藏数
          collect = response.css('span.bookmark-btn::text').extract()[0]
          match_re = re.match(".*?(\d+).*", collect)
          if match_re:
              collect = match_re.group(1)
          else:
              collect = 0
          # 评论数
          comment = response.css('a[href="#article-comment"] span::text').extract()[0]
          match_re = re.match(".*?(\d+).*", comment)
          if match_re:
              comment = match_re.group(1)
          else:
              comment = 0
          # 获得文章内容
          content = response.css("div.entry").extract()[0]
          # 获得标签
          tags = response.css("p.entry-meta-hide-on-mobile a::text").extract()
          tag = [element for element in tags if not element.strip().endswith("评论")]
          tags = ",".join(tag)
  ```

#### 2.item

> 相当于定义model

* 在items.py文件中定义item

  ```python
  class JobBoleArticleItem(scrapy.Item):
      title = scrapy.Field() #scrapy可以使用Field表示任意类型
      create_date = scrapy.Field()
      url = scrapy.Field()
      url_object_id = scrapy.Field() #对url进行编码
      front_image_url = scrapy.Field()
      front_image_path = scrapy.Field()
      praise_nums = scrapy.Field()
      comment_nums = scrapy.Field()
      fav_nums = scrapy.Field()
      tags = scrapy.Field()
      content = scrapy.Field()
  ```

* 在jobbole.py文件中定义爬虫返回内容放到item中

  ```python
  # -*- coding: utf-8 -*-
  import scrapy
  import re
  from scrapy.http import Request
  from urllib import parse
  
  #引入item
  from ArticleSpider.items import JobBoleArticleItem
  
  class JobboleSpider(scrapy.Spider):
      name = 'jobbole'
      allowed_domains = ['blog.jobbole.com']
      start_urls = ['http://blog.jobbole.com/all-posts/'] #放入想爬取的所有url
  
      def parse(self, response):
          """
          1.获取文章列表页中的文章url并交给scrapy下载后并进行解析
          2.获取下一页url并交给scrapy进行下载，下载完成后交给parse
          :param response:
          :return:
          """
  
          #解析列表页的所有文章url并交给scrapy下载后进行解析
          #利用::attr()伪类选择器获得对应元素的属性值
          post_nodes = response.css("#archive .floated-thumb .post-thumb a")
          for post_node in post_nodes:
              image_url = post_node.css("img::attr(src)").extract_first("") #获得图片的src
              post_url = post_node.css("::attr(href)").extract_first("") #获得连接的href
              #利用Request方法提交请求获取对应url内容
              #url表示访问的url(parse.urljoin是借助urllib将当前url与请求url进行拼接,从而获取到真实的url),callback表示回调的函数
              yield Request(url=parse.urljoin(response.url,post_url),meta={"front_image_url":image_url},callback=self.parse_detail)
  
          #提交下一页并交给scrapy进行下载
          #两个类之间有空格则表示子元素,两个类中间没空格则表示同时满足两个类的元素
          next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
          if next_url:
              yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)
  
      #提取文章的具体字段
      def parse_detail(self,response):
          ######################
          ## 利用css选择器获取内容
          ######################
          # 实例化item
          article_item = JobBoleArticleItem()
          # 获得meta中的front_image_url,文章封面图
          front_image_url = response.meta.get("front_image_url","")
          # 获得title
          title = response.css(".entry-header h1::text").extract()[0]
          print(title)
          create_date = response.css("p.entry-meta-hide-on-mobile::text").extract()[0].strip().replace("·", "").strip()
          # 点赞数
          praise_nums = response.css(".vote-post-up h10::text").extract()[0]
          # 收藏数
          collect = response.css('span.bookmark-btn::text').extract()[0]
          match_re = re.match(".*?(\d+).*", collect)
          if match_re:
              collect = match_re.group(1)
          else:
              collect = 0
          # 评论数
          comment = response.css('a[href="#article-comment"] span::text').extract()[0]
          match_re = re.match(".*?(\d+).*", comment)
          if match_re:
              comment = match_re.group(1)
          else:
              comment = 0
          # 获得文章内容
          content = response.css("div.entry").extract()[0]
          # 获得标签
          tags = response.css("p.entry-meta-hide-on-mobile a::text").extract()
          tag = [element for element in tags if not element.strip().endswith("评论")]
          tags = ",".join(tag)
  
          #填充item
          article_item['title'] = title
          article_item['url'] = response.url
          article_item['create_date'] = create_date
          article_item['front_image_url'] = [front_image_url]
          article_item['praise_nums'] = praise_nums
          article_item['comment_nums'] = comment
          article_item['fav_nums'] = collect
          article_item['tags'] = tags
          article_item['content'] = content
  
          yield article_item #将item传递到pipeline中
  ```

#### 3.pipeline

> * pipeline主要用于做数据处理
>
> * item赋值之后就会传递到pipeline.py中，但需要将settings中的
>
>   ```python
>   ITEM_PIPELINES = {
>      'ArticleSpider.pipelines.ArticlespiderPipeline': 300,
>   }
>   ```
>
>   取消注释
>
> * 在settings中设置下载图片的pipeline(scrapy已经给提供了,在site-package->scrapy->pipelines->images.py->ImagesPipeline),添加到配置的ITEM_PIPELINES中(为item流经的管道,后面的数字表示处理顺序,数字越小就越早进入pipeline)
>
>   ```python
>   #先进入ImagePipeline再进入ArticleSpiderPipeline
>   ITEM_PIPELINES = {
>      'ArticleSpider.pipelines.ArticlespiderPipeline': 300,
>      'scrapy.pipelines.images.ImagesPipeline': 1,
>   }
>   ```
>
> * ImagePipeline主要用于存储图片,需要在setting中配置下载传递item中的哪个字段，想保存图片还需要安装PIL库`pip install pillow`
>
>   ```python
>   import os
>   #先进入ImagePipeline再进入ArticleSpiderPipeline
>   ITEM_PIPELINES = {
>      'ArticleSpider.pipelines.ArticlespiderPipeline': 300,
>      'scrapy.pipelines.images.ImagesPipeline': 1,
>   }
>   #配置下载的是哪些字段,将指定的字段视作一个数组,故item中图片url应为数组格式
>   IMAGES_URLS_FIELD = "front_image_url"
>   #设置图片保存路径[先创建一个images文件夹]
>   project_dir = os.path.abspath(os.path.dirname(__file__)) #获得当前文件夹的绝对路径
>   IMAGES_STORE = os.path.join(project_dir,"images")
>   ```
>
> * 此时执行main.py会发现在images文件夹下会存储对应的网络图片

* 自定义存储图片pipeline

  * 配置setting.py，设置过滤掉的图片（表示必须大于100*100）

    ```python
    ITEM_PIPELINES = {
       'ArticleSpider.pipelines.ArticlespiderPipeline': 300,
       'scrapy.pipelines.images.ImagesPipeline': 1,
    }
    
    IMAGES_URLS_FIELD = "front_image_url"
    project_dir = os.path.abspath(os.path.dirname(__file__))
    IMAGES_STORE = os.path.join(project_dir,"images")
    # 表示下载的图片必须要是大于100*100的
    #IMAGES_MIN_HEIGHT = 100 #在ImagesPipeline中使用到了此变量
    #IMAGES_MIN_WIDTH = 100 #在ImagesPipeline中使用到了此变量
    ```

  * ImagesPipeline中的item_completed函数中可以获取到图片的实际下载地址（需要重载）

  * pipelines.py实例代码

    ```python
    # -*- coding: utf-8 -*-
    
    # Define your item pipelines here
    #
    # Don't forget to add your pipeline to the ITEM_PIPELINES setting
    # See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
    from scrapy.pipelines.images import ImagesPipeline
    
    class ArticlespiderPipeline(object):
        def process_item(self, item, spider):
            return item
    
    # 继承ImagePipeline
    class ArticleImagePipeline(ImagesPipeline):
        def item_completed(self, results, item, info):
            # result中包含一个tuple,一个是状态值,一个是返回对象
            for ok,value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path
            return item
    ```

* 自定义存储json的pipeline

  * setting.py配置调用pipeline

    ```python
    ITEM_PIPELINES = {
       'ArticleSpider.pipelines.ArticlespiderPipeline': 300,
       'ArticleSpider.pipelines.JsonWithEncodingPipeline': 2, #添加存储到json文件的pipeline
       'ArticleSpider.pipelines.ArticleImagePipeline': 1,
       # 'scrapy.pipelines.images.ImagesPipeline': 1,
    }
    ```

  * pipelines.py配置存储json的pipeline

    ```python
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
    ```

    * 首先利用codecs.open打开文件
    * 使用write方法将转换的json写入
    * 使用file的close方法关闭文件写入

  * scrapy提供了方便的exporters机制,帮助我们很方便的将item导出成各种类型的文件[前提是setting.py中调用此pipeline,此处省略去写]

    ```python
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
    ```

    * 使用open方法打开文件并创建exporter
    * 执行exporter的start_exporting方法开启exporter
    * 执行exporter的export_item方法将item写入exporter
    * 执行exporter的finish_exporting方法结束export
    * 关闭文件

#### 4.使用MySQL存储数据

* 修改jobbole.py中的create_date为date类型(便于存储到mysql中的date类型)

* 创建sql表

  ![](/Users/wangzhe/Practice/python分布式爬虫打造搜索引擎/第一章/表结构.png)

* 安装mysql驱动`pip install mysqlclient`

* 定义数据存储pipeline，直接将item存储到mysql中

  ```python
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
  ```

* 上述方法(execute和commit操作是同步操作)在后期爬取加解析会快于数据存储到mysql,会导致阻塞。使用twisted框架提供的api可以完成数据的异步写入。

  * 在setting.py中配置相关数据信息

    ```python
    MYSQL_HOST = "127.0.0.1"
    MYSQL_DBNAME = "scrapy"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "123456"
    ```

  * 使用twisted框架实现异步的数据写入

    ```python
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
    ```

#### 5.使用ItemLoader对item进行统一管理初试

* 设计思路
  * 使用**itemLoader**统一使用**add_css/add_xpath/add_value**方法获取对应数据并存储到item中
  * 在item中使用scrapy.Field的参数**input_processor**执行**MapCompose**方法执行对输入值的多次函数处理

* jobbole.py

  ```python
  # -*- coding: utf-8 -*-
  import scrapy
  import re
  from scrapy.http import Request
  from urllib import parse
  import datetime
  from scrapy.loader import ItemLoader
  
  #引入item
  from ArticleSpider.items import JobBoleArticleItem
  #引入md5处理url
  from ArticleSpider.utils.common import get_md5
  
  class JobboleSpider(scrapy.Spider):
      name = 'jobbole'
      allowed_domains = ['blog.jobbole.com']
      start_urls = ['http://blog.jobbole.com/all-posts/'] #放入想爬取的所有url
  
      def parse(self, response):
          """
          1.获取文章列表页中的文章url并交给scrapy下载后并进行解析
          2.获取下一页url并交给scrapy进行下载，下载完成后交给parse
          :param response:
          :return:
          """
  
          #解析列表页的所有文章url并交给scrapy下载后进行解析
          #利用::attr()伪类选择器获得对应元素的属性值
          post_nodes = response.css("#archive .floated-thumb .post-thumb a")
          for post_node in post_nodes:
              image_url = post_node.css("img::attr(src)").extract_first("") #获得图片的src
              post_url = post_node.css("::attr(href)").extract_first("") #获得连接的href
              #利用Request方法提交请求获取对应url内容
              #url表示访问的url(parse.urljoin是借助urllib将当前url与请求url进行拼接,从而获取到真实的url),callback表示回调的函数
              yield Request(url=parse.urljoin(response.url,post_url),meta={"front_image_url":image_url},callback=self.parse_detail)
  
          #提交下一页并交给scrapy进行下载
          #两个类之间有空格则表示子元素,两个类中间没空格则表示同时满足两个类的元素
          next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
          if next_url:
              yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)
  
      #提取文章的具体字段
      def parse_detail(self,response):
          ######################
          ## 利用css选择器获取内容
          ######################
          # 实例化item
          article_item = JobBoleArticleItem()
          # 获得meta中的front_image_url,文章封面图
          front_image_url = response.meta.get("front_image_url","")
          # 获得title
          title = response.css(".entry-header h1::text").extract()[0]
          print(title)
          create_date = response.css("p.entry-meta-hide-on-mobile::text").extract()[0].strip().replace("·", "").strip()
          # 点赞数
          praise_nums = response.css(".vote-post-up h10::text").extract()[0]
          # 收藏数
          collect = response.css('span.bookmark-btn::text').extract()[0]
          match_re = re.match(".*?(\d+).*", collect)
          if match_re:
              collect = match_re.group(1)
          else:
              collect = 0
          # 评论数
          comment = response.css('a[href="#article-comment"] span::text').extract()[0]
          match_re = re.match(".*?(\d+).*", comment)
          if match_re:
              comment = match_re.group(1)
          else:
              comment = 0
          # 获得文章内容
          content = response.css("div.entry").extract()[0]
          # 获得标签
          tags = response.css("p.entry-meta-hide-on-mobile a::text").extract()
          tag = [element for element in tags if not element.strip().endswith("评论")]
          tags = ",".join(tag)
  
          #填充item
          article_item['title'] = title
          #判断是否有日期,有的话则格式化成对应格式,没有的话则是当前日期
          try:
              create_date = datetime.datetime.strptime(create_date,"%Y%m%d").date()
          except Exception as e:
              create_date = datetime.datetime.now().date()
          article_item['create_date'] = create_date
          article_item['url'] = response.url
          article_item['url_object_id'] = get_md5(response.url)
          article_item['front_image_url'] = [front_image_url]
          article_item['praise_nums'] = praise_nums
          article_item['comment_nums'] = comment
          article_item['fav_nums'] = collect
          article_item['tags'] = tags
          article_item['content'] = content
  
  
          #Item loader加载item
          item_loader = ItemLoader(item=JobBoleArticleItem(),response=response)
          #使用css方式向item loader中填充值
          item_loader.add_css("title",".entry-header h1::text")
          item_loader.add_css("create_date","p.entry-meta-hide-on-mobile::text")
          item_loader.add_css("praise_nums",".vote-post-up h10::text")
          item_loader.add_css("comment_nums","a[href='#article-comment'] span::text")
          item_loader.add_css("fav_nums","span.bookmark-btn::text")
          item_loader.add_css("tags","p.entry-meta-hide-on-mobile a::text")
          item_loader.add_css("content","div.entry")
          #使用value方式向item_loader中填充值
          item_loader.add_value("url",response.url)
          item_loader.add_value("url_object_id",get_md5(response.url))
          item_loader.add_value("front_image_url",[front_image_url])
          article_item = item_loader.load_item()
          yield article_item #将item传递到pipeline中
  ```

  * 使用ItemLoader加载item，并使用add_css/add_xpath/add_value方法添加数值

* items.py

  ```python
  # -*- coding: utf-8 -*-
  
  # Define here the models for your scraped items
  #
  # See documentation in:
  # https://doc.scrapy.org/en/latest/topics/items.html
  
  import scrapy
  from scrapy.loader.processors import MapCompose
  
  class ArticlespiderItem(scrapy.Item):
      # define the fields for your item here like:
      # name = scrapy.Field()
      pass
  
  #处理的函数,value表示input的值,即初始值
  def add_jobbole(value):
      return value+"-jobbole"
  
  class JobBoleArticleItem(scrapy.Item):
      title = scrapy.Field(
          input_processor = MapCompose(add_jobbole) #Mapcompose表示可以对传入的内容调用多个函数进行预处理
      ) #scrapy可以使用Field表示任意类型
      create_date = scrapy.Field()
      url = scrapy.Field()
      url_object_id = scrapy.Field() #对url进行编码
      front_image_url = scrapy.Field()
      front_image_path = scrapy.Field()
      praise_nums = scrapy.Field()
      comment_nums = scrapy.Field()
      fav_nums = scrapy.Field()
      tags = scrapy.Field()
      content = scrapy.Field()
  ```

  * 使用MapCompose方法多次调用执行函数

#### 6.使用ItemLoader对item进行统一调整并通过配置item实现数据处理

* items.py添加对字段的处理内容

  ```python
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
  ```

* pipelines.py调整内容,在ArticleImagePipeline中添加对item中是否有front_image_url的判断

  ```python
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
              cursorclass = MySQLdb.cursors.DictCursor,
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
  ```

* jobbole.py文件中通过itemloader处理item并进行传递

  ```python
  # -*- coding: utf-8 -*-
  import scrapy
  import re
  from scrapy.http import Request
  from urllib import parse
  import datetime
  
  #引入item
  from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader
  #引入md5处理url
  from ArticleSpider.utils.common import get_md5
  
  class JobboleSpider(scrapy.Spider):
      name = 'jobbole'
      allowed_domains = ['blog.jobbole.com']
      start_urls = ['http://blog.jobbole.com/all-posts/'] #放入想爬取的所有url
  
      def parse(self, response):
          """
          1.获取文章列表页中的文章url并交给scrapy下载后并进行解析
          2.获取下一页url并交给scrapy进行下载，下载完成后交给parse
          :param response:
          :return:
          """
  
          #解析列表页的所有文章url并交给scrapy下载后进行解析
          #利用::attr()伪类选择器获得对应元素的属性值
          post_nodes = response.css("#archive .floated-thumb .post-thumb a")
          for post_node in post_nodes:
              image_url = post_node.css("img::attr(src)").extract_first("") #获得图片的src
              post_url = post_node.css("::attr(href)").extract_first("") #获得连接的href
              #利用Request方法提交请求获取对应url内容
              #url表示访问的url(parse.urljoin是借助urllib将当前url与请求url进行拼接,从而获取到真实的url),callback表示回调的函数
              yield Request(url=parse.urljoin(response.url,post_url),meta={"front_image_url":image_url},callback=self.parse_detail)
  
          #提交下一页并交给scrapy进行下载
          #两个类之间有空格则表示子元素,两个类中间没空格则表示同时满足两个类的元素
          next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
          if next_url:
              yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)
  
      #提取文章的具体字段
      def parse_detail(self,response):
          ######################
          ## 利用css选择器获取内容
          ######################
          # 实例化item
          article_item = JobBoleArticleItem()
          # 获得meta中的front_image_url,文章封面图
          front_image_url = response.meta.get("front_image_url","")
          # 获得title
          title = response.css(".entry-header h1::text").extract()[0]
          print(title)
          create_date = response.css("p.entry-meta-hide-on-mobile::text").extract()[0].strip().replace("·", "").strip()
          # 点赞数
          praise_nums = response.css(".vote-post-up h10::text").extract()[0]
          # 收藏数
          collect = response.css('span.bookmark-btn::text').extract()[0]
          match_re = re.match(".*?(\d+).*", collect)
          if match_re:
              collect = match_re.group(1)
          else:
              collect = 0
          # 评论数
          comment = response.css('a[href="#article-comment"] span::text').extract()[0]
          match_re = re.match(".*?(\d+).*", comment)
          if match_re:
              comment = match_re.group(1)
          else:
              comment = 0
          # 获得文章内容
          content = response.css("div.entry").extract()[0]
          # 获得标签
          tags = response.css("p.entry-meta-hide-on-mobile a::text").extract()
          tag = [element for element in tags if not element.strip().endswith("评论")]
          tags = ",".join(tag)
  
          #填充item
          article_item['title'] = title
          #判断是否有日期,有的话则格式化成对应格式,没有的话则是当前日期
          try:
              create_date = datetime.datetime.strptime(create_date,"%Y%m%d").date()
          except Exception as e:
              create_date = datetime.datetime.now().date()
          article_item['create_date'] = create_date
          article_item['url'] = response.url
          article_item['url_object_id'] = get_md5(response.url)
          article_item['front_image_url'] = [front_image_url]
          article_item['praise_nums'] = praise_nums
          article_item['comment_nums'] = comment
          article_item['fav_nums'] = collect
          article_item['tags'] = tags
          article_item['content'] = content
  
  
          #Item loader加载item
          item_loader = ArticleItemLoader(item=JobBoleArticleItem(),response=response)
          #使用css方式向item loader中填充值
          item_loader.add_css("title",".entry-header h1::text")
          item_loader.add_css("create_date","p.entry-meta-hide-on-mobile::text")
          item_loader.add_css("praise_nums",".vote-post-up h10::text")
          item_loader.add_css("comment_nums","a[href='#article-comment'] span::text")
          item_loader.add_css("fav_nums","span.bookmark-btn::text")
          item_loader.add_css("tags","p.entry-meta-hide-on-mobile a::text")
          item_loader.add_css("content","div.entry")
          #使用value方式向item_loader中填充值
          item_loader.add_value("url",response.url)
          item_loader.add_value("url_object_id",get_md5(response.url))
          item_loader.add_value("front_image_url",[front_image_url])
          article_item = item_loader.load_item()
          yield article_item #将item传递到pipeline中
  ```

  