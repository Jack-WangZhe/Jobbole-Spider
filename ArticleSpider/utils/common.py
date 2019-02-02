import hashlib

# 对url进行md5处理
def get_md5(url):
    # 在python3中所有内存中的字符串都是unicode编码,但是unicode编码的字符串是没法使用md5处理的
    # 所以我们需要先判断url是不是unicode(str表示的就是unicode),如果是的话需要进行编码
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    #返回md5处理过的摘要生成
    return m.hexdigest()

if __name__ == "__main__":
    print(get_md5("http://jobbole.com".encode("utf-8")))