from bs4 import BeautifulSoup
import mysql.connector
import time
import random
import re
import json
import requests
from requests.exceptions import SSLError
import tkinter as tk
from tkinter import messagebox

from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage

# 星火认知大模型Spark3.5 Max的URL值，其他版本大模型URL值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_URL = 'wss://spark-api.xf-yun.com/v1.1/chat'
# 星火认知大模型调用秘钥信息，请前往讯飞开放平台控制台（https://console.xfyun.cn/services/bm35）查看
SPARKAI_APP_ID = 'c3ad6fa7'
SPARKAI_API_SECRET = 'MmFhNmY4ZDZiZDEwMjkzYmUxZDc5NTlh'
SPARKAI_API_KEY = '3da9a6c9584eb9db8959b4e651ff1322'
# 星火认知大模型Spark3.5 Max的domain值，其他版本大模型domain值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_DOMAIN = 'general'

spark = ChatSparkLLM(
    spark_api_url=SPARKAI_URL,
    spark_app_id=SPARKAI_APP_ID,
    spark_api_key=SPARKAI_API_KEY,
    spark_api_secret=SPARKAI_API_SECRET,
    spark_llm_domain=SPARKAI_DOMAIN,
    streaming=False,
)


def random_sleep():
    # 生成一个随机延时，单位为秒
    delay = random.uniform(1, 3)
    time.sleep(delay)


class Crawler:
    def __init__(self, db_config):
        self.connection = None
        self.db_config = db_config

    def connect_to_mysql(self):
        """连接到 MySQL 数据库"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            print("数据库连接成功...")

        except mysql.connector.Error as error:
            print(f"Error connecting to MySQL: {error}")

    def close_connection(self):
        """关闭数据库连接"""
        try:
            if self.connection and self.connection.is_connected():
                self.connection.close()
                print("数据库已关闭连接...")

        except mysql.connector.Error as error:
            print(f"Error closing MySQL connection: {error}")

    def search_all_people(self):
        """在数据库中搜索所有的人员信息"""
        try:
            cursor = self.connection.cursor()  # type: ignore
            sql = "SELECT * FROM people"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

        except mysql.connector.Error as error:
            print(f"Error searching people: {error}")
            return None

    def print_person(self):
        print("以下是所有教授名单: ")
        # 调用函数并打印结果
        all_people = self.search_all_people()
        if all_people:
            for person in all_people:
                print(person)
            print("结束...")

    def get_row_count(self):
        try:
            cursor = self.connection.cursor()  # type: ignore
            sql = "SELECT COUNT(*) FROM people"
            cursor.execute(sql)
            result = cursor.fetchone()[0]  # type: ignore # 获取结果集的第一行第一列的值
            return result
        except mysql.connector.Error as error:
            print(f"Error fetching row count: {error}")
            return None

    def update_info(self):
        """遍历输出 people 表中的 profileurl 数据"""
        # 连接到 MySQL 数据库
        self.connect_to_mysql()
        try:
            cursor = self.connection.cursor()  # type: ignore
            sql = "SELECT profileurl FROM people"
            cursor.execute(sql)
            profile_urls = cursor.fetchall()
            count = 1
            for profileurl in profile_urls:
                # 调整访问频率
                # random_sleep()

                print(
                    '-------------------------------------------------------------------------------------------------------------')
                print(profileurl[0])  # type: ignore
                name, emails, field = self.get_name_emails_field_from_page(profileurl[0])  # type: ignore
                self.update_info_from_profileurl(name, emails, field, count)
                count += 1
            print(f"一共修改了{count}行数据")

        except mysql.connector.Error as error:
            print(f"Error searching profile URLs: {error}")

    def update_info_from_profileurl(self, name, emails, field, count):
        try:
            cursor = self.connection.cursor()  # type: ignore
            sql = "update people set name = %s, email = %s, field = %s where id = %s"
            params = (name, emails, field, count)
            cursor.execute(sql, params)
            self.connection.commit()  # type: ignore
            print(f"修改第{count}条数据{params}成功")
        except mysql.connector.Error as error:
            print(f"Error updating profile URLs: {error}")

    def insert_person2(self, profileurl, name, emails, field, school, department, location):
        """向数据库中插入一条 URL 记录"""
        try:
            cursor = self.connection.cursor()  # type: ignore

            # 定义参数
            params = (profileurl, name, emails, field, school, department, location)
            sql = "INSERT INTO people2 (profileurl,name,email,field,school,department,location) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, params)
            self.connection.commit()  # type: ignore
            print(f"插入{params}成功...")

        except mysql.connector.Error as error:
            print(f"Error inserting URL: {error}")

    def crawler(self):
        """主要爬取数据方法"""
        # 连接到 MySQL 数据库
        self.connect_to_mysql()

        # TODO 【1】这里需要修改学校的网址
        school = ""
        department = ""
        location = ""
        # # 发送请求并获取页面内容
        for i in range(1, 2):  # i代表页面
            cursor = self.connection.cursor()
            cursor.execute("SELECT website FROM websites")
            websites = cursor.fetchall()
            for url in websites:
                if url:
                    url = url[0]
                    print(url)
                    response = requests.get(url)
                    html_content = response.text
                    print(html_content)
                    # 使用 BeautifulSoup 解析页面内容
                    soup = BeautifulSoup(html_content, 'html.parser')
                    # print(soup.text)

                    # 创建一个集合来存储href属性值，用于去重
                    href_set = set()
                    count = 0
                    # # 定义正则表达式模式
                    # pattern = r"edu/[^/]+$"
                    # and re.match(pattern, href)
                    # 找到所有的<a>标签并筛选包含"/directory/"的标签
                    for a_tag in soup.find_all('a'):
                        # 调整睡眠时间
                        # random_sleep()
                        href = a_tag.get('href')
                        print(f"href: {href}")
                        # TODO 【1】检查href属性值是否包含"/something/"
                        if href and (
                                "/staff/" in href or "/faculty-staff/" in href or "/user" in href or "/staffs/" in href or "/faculty" in href or "/profile" in href or "/team/" in href or "/person/" in href or "/research-group/" in href or "/directory" in href or "/people/" in href or "/profile/" in href) and href not in href_set:
                            href_set.add(href)
                            # href = href.split("/people/")[0].split("/")[0]
                            # TODO 【2】注意这里也要改 url
                            pre = url
                            if "www" in href or "http" in href:  # 避免已经存在前缀url
                                profileurl = href
                            else:
                                profileurl = pre + href
                            print(
                                '-------------------------------------------------------------------------------------------------------------')
                            print(f'现在访问的profileurl: {profileurl}')
                            name, emails, field = self.get_name_emails_field_from_page(profileurl)
                            count += 1
                            print(
                                f"现在是第{count}条数据:\n profileurl: {profileurl}\n name: {name} \n emails: {emails}\n field: {field}\n school: {school}\n department: {department}\n location: {location}")
                            print(
                                '-------------------------------------------------------------------------------------------------------------')
                            # self.insert_person(profileurl, name, emails, field, school, department, location)
                            self.insert_person2(profileurl, name, emails, field, school, department, location)



        # 关闭数据库连接
        self.close_connection()

    def print_profileurl_name_email_field_form_page(self):
        """遍历输出 people 表中的 profileurl 数据"""
        # 连接到 MySQL 数据库
        self.connect_to_mysql()
        try:
            cursor = self.connection.cursor()  # type: ignore
            sql = "SELECT profileurl FROM people"
            cursor.execute(sql)
            profile_urls = cursor.fetchall()
            print("以下是所有教授的 profileurl,以及对应的name,email,field：")
            count = 0
            for url in profile_urls:
                print(f"现在是第{count + 1}条数据")
                print(f"profileurl: {url[0]}")  # type: ignore

                name, emails, field = self.get_name_emails_field_from_page(url[0])  # type: ignore
                print(f"name:{name}, emails: {emails}, field: {field}")
                print('--------------------------------------------')
                count += 1
            print(f"一共有{count}行数据")

        except mysql.connector.Error as error:
            print(f"Error printing profile URLs: {error}")

    def get_name_emails_field_from_page(self, profileurl):
        """从页面中获取所有电子邮件地址"""
        try:
            # 发送请求并获取页面内容
            response = requests.get(profileurl)
            html_content = response.text
            # 使用Beautiful Soup解析HTML内容
            soup = BeautifulSoup(response.content, 'html.parser')
            # 查找研究方向信息，这里假设研究方向信息在页面的段落中
            paragraphs = soup.find_all('p')

            research_direction = self.handle_field(paragraphs)

            # 使用正则表达式匹配电子邮件地址的模式
            pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

            # 查找姓名信息，这里假设姓名信息在页面标题中
            name = soup.title.string  # getnamefrompage type: ignore
            name = self.handle_name(name)
            # 在页面内容中查找匹配的电子邮件地址
            emails = re.findall(pattern, html_content)

            # 找到所有的链接标签
            links = soup.find_all('a')
            # 提取以 'mailto:' 开头的链接，并获取邮箱地址
            for link in links:
                href = link.get('href')
                if href and href.startswith('mailto:'):
                    email = href.split(':')[1]
                    # print(email)
                    emails.append(email)

            # emails = self.handle_email(emails)
            if not emails:
                return name, "", research_direction
            else:
                return name, ', '.join(set(emails)), research_direction
        except SSLError as e:
            print("SSL 连接错误:", e)
            # 这里可以处理 SSL 连接错误的情况
            return "", "", ""
        except Exception as e:
            print("其他异常:", e)
            # 这里可以处理其他异常的情况
            return "", "", ""

    def handle_name(self, name):
        try:
            messages = [ChatMessage(
                role="user",
                content=f'请你给出这个人{name}的名字，只需要给出名字即可，其他任何的都不需要！！！'
            )]
            handler = ChunkPrintHandler()
            name = spark.generate([messages], callbacks=[handler]).generations[0][0].text
            print(name)

            return name
        except Exception as e:
            print("发生错误:", e)
            return None

    def handle_field(self, field):
        try:

            messages = [ChatMessage(
                role="user",
                content=f'请你给出{field}中的主要领域，如果没有，就返回None，其他任何的都不需要！！！'
            )]
            handler = ChunkPrintHandler()
            field = spark.generate([messages], callbacks=[handler]).generations[0][0].text
            print(field)

            return field
        except Exception as e:
            print("发生错误:", e)
            return None

    def handle_email(self, email):
        try:

            messages = [ChatMessage(
                role="user",
                content=f'请你给出这个人{email}的邮件，只需要给出邮件，其他任何的都不需要！！！'
            )]
            handler = ChunkPrintHandler()
            email = spark.generate([messages], callbacks=[handler]).generations[0][0].text
            print(email)

            return email
        except Exception as e:
            print("发生错误:", e)
            return None

    # TODO 数据爬取结束再进行此操作
    def remove_duplicates(self):
        """去重url"""
        try:
            cursor = self.connection.cursor()  # type: ignore

            # 创建临时表
            cursor.execute("CREATE TEMPORARY TABLE temp_urls LIKE urls")

            # 将唯一的 URL 复制到临时表中
            cursor.execute("INSERT INTO temp_urls SELECT DISTINCT url FROM urls")

            # 清空原始表
            cursor.execute("TRUNCATE TABLE urls")

            # 将唯一的 URL 从临时表插入回原始表中
            cursor.execute("INSERT INTO urls SELECT * FROM temp_urls")

            # 删除临时表
            cursor.execute("DROP TABLE temp_urls")

            print("表去重成功...")

            # 提交事务
            self.connection.commit()  # type: ignore

        except mysql.connector.Error as error:
            print(f"Error printing profile URLs: {error}")

    def get_all_a_tags(self):
        """获取页面中的所有 <a> 标签"""
        try:
            # 发送请求并获取页面内容
            url = input("请输入某一个页面的地址，以获取这个页面所有的a标签:\n")
            # 发送请求并获取页面内容
            response = requests.get(url)
            html_content = response.text

            # 使用 BeautifulSoup 解析页面内容
            soup = BeautifulSoup(html_content, 'html.parser')

            # 查找页面中的所有 <a> 标签
            a_tags = soup.find_all('a')

            # 遍历所有 <a> 标签，并逐个打印其 href 属性值
            for a_tag in a_tags:
                href = a_tag.get('href')
                if href:
                    print(href)

        except Exception as e:
            print(f"Error fetching <a> tags from page: {e}")


# 数据库配置
db_config = {
    "host": "localhost",
    "user": "admin",
    "password": "123456",
    "database": "outsourcing"
}

field_keywords = ['方向', '兴趣', '研究方向', 'research', 'Research Summary', 'direction', 'research_direction',
                  'field',
                  'main field', 'interests', '研究兴趣', '领域', 'bio',
                  '主要领域', '主要方向']

# 记录开始时间
start_time = time.time()

# 实例化爬虫对象
crawler = Crawler(db_config)

# 启动爬虫，爬取各位教授的简介profileurl
crawler.crawler()

# 记录结束时间
end_time = time.time()

# 计算运行时间
elapsed_time = end_time - start_time
print(f"代码运行时间: {elapsed_time} 秒")
# 弹出提示信息
messagebox.showinfo("提示", f"代码运行时间: {elapsed_time} 秒")
