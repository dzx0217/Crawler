import random
import sys
import time

import requests
from bs4 import BeautifulSoup


def fetch_pubmed_data(keyword):
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"
    search_params = {
        'term': keyword,
        'filter': 'datesearch.y_5'
    }
    simulate_task(100)
    search_response = requests.get(base_url, params=search_params)
    if search_response.status_code != 200:
        raise Exception("Failed to load page {}".format(base_url))

    search_soup = BeautifulSoup(search_response.text, 'html.parser')

    articles = []
    for docsum in search_soup.find_all('div', class_='docsum-content'):
        title_tag = docsum.find('a', class_='docsum-title')
        journal_citation_tag = docsum.find('span', class_='docsum-journal-citation full-journal-citation')
        pmid_tag = docsum.find('span', class_='docsum-pmid')

        if title_tag and journal_citation_tag and pmid_tag:
            pmid = pmid_tag.get_text(strip=True)
            article = {
                'title': title_tag.get_text(strip=True),
                'journal_citation': journal_citation_tag.get_text(strip=True),
                'pmid': pmid,
                'abstract': fetch_abstract(pmid)
            }
            articles.append(article)

    return articles


def fetch_abstract(pmid):
    article_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    article_response = requests.get(article_url)
    if article_response.status_code != 200:
        raise Exception("Failed to load page {}".format(article_url))

    article_soup = BeautifulSoup(article_response.text, 'html.parser')
    abstract_tag = article_soup.find('div', class_='abstract-content selected')

    if abstract_tag:
        abstract_content = abstract_tag.find('p')
        if abstract_content:
            return abstract_content.get_text(strip=True)

    return "No abstract available"

def print_progress_bar(iteration, total, length=50):
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r|{bar}| {percent}% Complete')
    sys.stdout.flush()

def simulate_task(total_steps):
    for step in range(1, total_steps + 1):
        print_progress_bar(step, total_steps)
        time.sleep(0.1)  # 模拟任务的休眠时间
    print()  # 换行

def print_progress_bar(iteration, total, length=50):
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    # 设置前景色为白色
    white = '\x1b[37m'
    # 设置前景色为红色
    red = '\x1b[31m'
    # 重置颜色
    reset = '\x1b[0m'
    # 组合颜色和进度条字符
    colored_bar = f'{white}|{red}{bar}{reset}|'
    sys.stdout.write(f'\r{colored_bar} {percent}% Complete')
    sys.stdout.flush()

# 错误描述列表
error_descriptions = [
    "FileNotFoundError: [Errno 2] No such file or directory",
    "IndexError: list index out of range",
    "KeyError: 'key'",
    "TypeError: unsupported operand type(s)",
    "ValueError: invalid literal for int()",
    "NameError: name 'variable' is not defined",
    "AttributeError: 'object' has no attribute 'attribute'",
    "ZeroDivisionError: division by zero",
]


while True:
    # 使用示例
    keyword = "Eric Alm MIT"
    simulate_task(100)
    articles = fetch_pubmed_data(keyword)

    for article in articles:
        print(f"Title: {article['title']}")
        print(f"Journal Citation: {article['journal_citation']}")
        print(f"PMID: {article['pmid']}")
        print(f"Abstract: {article['abstract']}\n")

        # 使用示例
    for i in range(50):
        print_progress_bar(i, 100)
        if random.random() < 0.1:  # 10%的几率打印错误描述
            error_msg = random.choice(error_descriptions)
            sys.stdout.write(f'\n{error_msg}\n')
        time.sleep(0.1)  # 模拟时间延迟
