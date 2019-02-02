#execute函数可以执行scrapy脚本
from scrapy.cmdline import execute
#需要sys获得工程目录
import sys
import os
#需要设置工程目录,设置完工程目录之后调用execute函数才会生效
print(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#execute相当于执行命令
execute(["scrapy","crawl","jobbole"])