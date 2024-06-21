import mysql.connector
from translate import Translator
import re
import urllib.parse, urllib.request
import hashlib
import urllib
import random
import json
import time
from translate import Translator

appid = '20240621002081561'
secretKey = 'Zg3Rqk8wL0ITXQyB5z8a'
url_baidu = 'http://api.fanyi.baidu.com/api/trans/vip/translate'


def translateBaidu(text, f='zh', t='en'):
    salt = random.randint(32768, 65536)
    sign = appid + text + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    url = url_baidu + '?appid=' + appid + '&q=' + urllib.parse.quote(text) + '&from=' + f + '&to=' + t + \
          '&salt=' + str(salt) + '&sign=' + sign
    response = urllib.request.urlopen(url)
    content = response.read().decode('utf-8')
    data = json.loads(content)
    result = str(data['trans_result'][0]['dst'])
    print(result)
    return result


# 设置数据库连接
conn = mysql.connector.connect(
    host='localhost',
    user='admin',
    password='123456',
    database='outsourcing'
)

cursor = conn.cursor()

# 查找包含中文的记录
cursor.execute("SELECT id, field FROM people2")
records = cursor.fetchall()

# 更新每条记录
for record in records:
    id, field = record
    print(id)
    print(field)
    if id >= 15497:
        if field != '' and field is not None:
            translated_field = translateBaidu(field)
            if translated_field is not None:
                sql = "update people2 set field = %s where id = %s"
                params = (translated_field, id)
                cursor.execute(sql, params)

                # 提交更改
                conn.commit()

# 关闭连接
cursor.close()
conn.close()
