from bs4 import BeautifulSoup
import mysql.connector
import time
import random
import re
import json
import requests
from requests.exceptions import SSLError


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
            cursor = self.connection.cursor() # type: ignore
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

    def insert_url(self, profileurl, school, department, location):
        """向数据库中插入一条 URL 记录"""
        try:
            cursor = self.connection.cursor() # type: ignore
            # TODO 【0】(name,email,field)部分
            name = ""
            email = ""
            field = ""

            # 定义参数
            params = (profileurl, name, email, field, school, department, location)
            sql = "INSERT INTO people (profileurl,name,email,field,school,department,location) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, params)
            self.connection.commit() # type: ignore
            print(f"插入{params}成功...")

        except mysql.connector.Error as error:
            print(f"Error inserting URL: {error}")

    def url_crawler(self):
        # 连接到 MySQL 数据库
        self.connect_to_mysql()

        # TODO 【1】这里需要修改学校的网址
        school = "University of Cambridge"
        department = "化学工程与生物技术" + "学院"
        location = "UK"
        # 发送请求并获取页面内容
        url = 'https://www.ceb.cam.ac.uk/directory/post-doctoral-researchers'

        response = requests.get(url)
        html_content = response.text
        # 使用 BeautifulSoup 解析页面内容
        soup = BeautifulSoup(html_content, 'html.parser')
        # print(soup.text)

        # # 处理json格式以及ajax等行为
        # data_string = str(soup.text)
        # print(data_string)
        # # 匹配所有 "/people\/" 后面的单词，直到遇到下一个 `\`
        # matches = re.findall(r'/people\\/([^\\/]+)', data_string)
        # # 过滤掉不含有 "-" 的单词
        # filtered_matches = set([match for match in matches if '-' in match])
        #
        # for filtered_matche in filtered_matches:
        #     # print('https://imes.mit.edu/people/'+filtered_matche)
        #     self.insert_url('https://imes.mit.edu/people/' + filtered_matche, school, department)

        # 创建一个集合来存储href属性值，用于去重
        href_set = set()
        # 找到所有的<a>标签并筛选包含"/directory/"的标签
        for a_tag in soup.find_all('a'):
            href = a_tag.get('href')
            # TODO 【2】检查href属性值是否包含"/something/"
            if href and (
                    "/staff/" in href or "/directory/" in href or "/people/" in href or "/profile/" in href) and href not in href_set:
                href_set.add(href)
                # TODO 【3】注意这里也要改 url
                if "www" in href:  # 避免已经存在前缀url
                    profileurl = href
                else:
                    profileurl = 'https://www.ceb.cam.ac.uk/' + href
                print(f"profileurl: {profileurl}, school: {school}, department: {department}, location: {location}")
                # self.insert_url(profileurl, school, department, location)

        # 关闭数据库连接
        self.close_connection()

    def print_profileurl_name_email_field_form_page(self):
        """遍历输出 people 表中的 profileurl 数据"""
        # 连接到 MySQL 数据库
        self.connect_to_mysql()
        try:
            cursor = self.connection.cursor() # type: ignore
            sql = "SELECT profileurl FROM people"
            cursor.execute(sql)
            profile_urls = cursor.fetchall()
            print("以下是所有教授的 profileurl,以及对应的name,email,field：")
            count = 0
            for url in profile_urls:
                print(f"现在是第{count + 1}条数据")
                print(f"profileurl: {url[0]}") # type: ignore
                name, emails, field = self.get_name_emails_field_from_page(url[0]) # type: ignore
                print(f"name:{name}, emails: {emails}, field: {field}")
                count += 1
            print(f"一共有{count}行数据")

        except mysql.connector.Error as error:
            print(f"Error printing profile URLs: {error}")

    def get_name_emails_field_from_page(self, url):
        """从页面中获取所有电子邮件地址"""
        try:
            # 发送请求并获取页面内容
            response = requests.get(url)
            html_content = response.text
            # 使用Beautiful Soup解析HTML内容
            soup = BeautifulSoup(response.content, 'html.parser')
            # 查找研究方向信息，这里假设研究方向信息在页面的段落中
            paragraphs = soup.find_all('p')

            research_direction = None
            for p in paragraphs:
                text_lower = p.text.lower()  # 将文本转换为小写
                for keyword in keywords:
                    if keyword in text_lower:
                        research_direction = p.text
                        break
                if research_direction:
                    break

            # 使用正则表达式匹配电子邮件地址的模式
            pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

            # 查找姓名信息，这里假设姓名信息在页面标题中
            name = soup.title.string # type: ignore

            # 在页面内容中查找匹配的电子邮件地址
            emails = re.findall(pattern, html_content)

            return name, set(emails), research_direction
        except SSLError as e:
            print("SSL 连接错误:", e)
            # 这里可以处理 SSL 连接错误的情况
            return "", "", ""
        except Exception as e:
            print("其他异常:", e)
            # 这里可以处理其他异常的情况
            return "", "", ""


# 数据库配置
db_config = {
    "host": "localhost",
    "user": "admin",
    "password": "123456",
    "database": "professors"
}
# 研究方向关键字
keywords = ['research', 'interests', '兴趣', '研究兴趣', '领域', '研究领域', '主要领域', '方向', '主要方向', '研究方向']

# 实例化爬虫对象
crawler = Crawler(db_config)

# 启动爬虫，爬取各位教授的简profileurl
crawler.url_crawler()

# 启动爬虫,根据教授的简介url，找出这个教授的email
# crawler.print_profileurl_name_email_field_form_page()
