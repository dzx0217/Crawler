import time

import pymysql
import requests
from bs4 import BeautifulSoup

def fetch_pubmed_data(keyword):
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"
    search_params = {
        'term': keyword,
        'filter': 'datesearch.y_5'
    }
    # time.sleep(5)
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
    # time.sleep(5)
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


def get_people_data():
    connection = pymysql.connect(host='localhost',
                                 user='admin',
                                 password='123456',
                                 database='outsourcing',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id, name, school FROM people2 where id >= 2869"
            cursor.execute(sql)
            result = cursor.fetchall()
    finally:
        connection.close()

    return result


def insert_articles_data(articles_data):
    connection = pymysql.connect(host='localhost',
                                 user='admin',
                                 password='123456',
                                 database='outsourcing',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            for article in articles_data:
                sql = """INSERT INTO articles (personid, name, school, title, journal_citation, pmid, abstract)
                         VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (
                    article['personid'],
                    article['name'],
                    article['school'],
                    article['title'],
                    article['journal_citation'],
                    article['pmid'],
                    article.get('abstract', 'No abstract available')  # 使用get方法提供默认值
                ))
                connection.commit()
    finally:
        connection.close()


def main():
    people_data = get_people_data()
    all_articles = []

    for person in people_data:
        keyword = f"{person['name']} {person['school']}"
        print(keyword)
        articles = fetch_pubmed_data(keyword)
        print(articles)
        # 在main函数中
        for article in articles:
            article['personid'] = person['id']
            article['name'] = person['name']
            article['school'] = person['school']
            print(article['personid'])
            # 将单个文章作为一个列表传递给insert_articles_data函数
            insert_articles_data([article])
        all_articles.extend(articles)

    # insert_articles_data(all_articles)

if __name__ == "__main__":
    main()
