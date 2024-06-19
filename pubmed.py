import requests
from bs4 import BeautifulSoup


def fetch_pubmed_data(keyword):
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"
    search_params = {
        'term': keyword,
        'filter': 'datesearch.y_5'
    }

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


# 使用示例
keyword = "Eric Alm MIT"
articles = fetch_pubmed_data(keyword)

for article in articles:
    print(f"Title: {article['title']}")
    print(f"Journal Citation: {article['journal_citation']}")
    print(f"PMID: {article['pmid']}")
    print(f"Abstract: {article['abstract']}\n")
