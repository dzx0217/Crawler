import requests
from bs4 import BeautifulSoup

def fetch_pubmed_data(keyword):
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"
    params = {
        'term': keyword,
        'filter': 'datesearch.y_5'
    }

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        raise Exception("Failed to load page {}".format(base_url))

    soup = BeautifulSoup(response.text, 'html.parser')

    articles = []
    for docsum in soup.find_all('div', class_='docsum-content'):
        title_tag = docsum.find('a', class_='docsum-title')
        journal_citation_tag = docsum.find('span', class_='docsum-journal-citation full-journal-citation')
        pmid_tag = docsum.find('span', class_='docsum-pmid')

        if title_tag and journal_citation_tag and pmid_tag:
            article = {
                'title': title_tag.get_text(strip=True),
                'journal_citation': journal_citation_tag.get_text(strip=True),
                'pmid': pmid_tag.get_text(strip=True)
            }
            articles.append(article)

    return articles

# 使用示例
keyword = "cancer"
articles = fetch_pubmed_data(keyword)

for article in articles:
    print(f"Title: {article['title']}")
    print(f"Journal Citation: {article['journal_citation']}")
    print(f"PMID: {article['pmid']}\n")
