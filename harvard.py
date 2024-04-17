import requests
from bs4 import BeautifulSoup
import re

def scrape_faculty_info(url):
    # 发送 HTTP 请求获取网页内容
    response = requests.get(url)
    if response.status_code == 200:
        # 使用 BeautifulSoup 解析网页内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 使用正则表达式匹配教师信息
        faculty_info_pattern = re.compile(r'<div class="views-field views-field-title">(.*?)<div class="views-field views-field-field-email">(.*?)<div class="views-field views-field-field-biographical-information">(.*?)</div></div>', re.DOTALL)
        faculty_matches = faculty_info_pattern.findall(str(soup))
        
        # 提取教师的姓名、邮箱和研究领域
        faculty_info_list = []
        for match in faculty_matches:
            name = match[0].strip()
            email_matches = re.findall(r'[\w\.-]+@[\w\.-]+', match[1])
            email = email_matches[0] if email_matches else None
            research_areas = match[2].strip()
            faculty_info_list.append({'name': name, 'email': email, 'research_areas': research_areas})
        
        return faculty_info_list
    else:
        print(f'Failed to retrieve the webpage. Status code: {response.status_code}')
        return None

# 要爬取的网页 URL
url = 'https://dms.hms.harvard.edu/faculty'
# 爬取教师信息
faculty_info = scrape_faculty_info(url)
if faculty_info:
    for info in faculty_info:
        print(f"姓名: {info['name']}")
        print(f"邮箱: {info['email']}")
        print(f"研究领域: {info['research_areas']}")
        print()