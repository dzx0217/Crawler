import pandas as pd
from metapub import PubMedFetcher

# initialise the keyword to be searched and number of articles to be retrieved

keyword = "sepsis"
num_of_articles = 3

fetch = PubMedFetcher()

# get the  PMID for first 3 articles with keyword sepsis
pmids = fetch.pmids_for_query(keyword, retmax=num_of_articles)

# get  articles
articles = {}
for pmid in pmids:
    articles[pmid] = fetch.article_by_pmid(pmid)

# get title for each article:
titles = {}
for pmid in pmids:
    titles[pmid] = fetch.article_by_pmid(pmid).title
Title = pd.DataFrame(list(titles.items()), columns=['pmid', 'Title'])
Title

# get abstract for each article:
abstracts = {}
for pmid in pmids:
    abstracts[pmid] = fetch.article_by_pmid(pmid).abstract
Abstract = pd.DataFrame(list(abstracts.items()), columns=['pmid', 'Abstract'])
Abstract

# get author for each article:
authors = {}
for pmid in pmids:
    authors[pmid] = fetch.article_by_pmid(pmid).authors
Author = pd.DataFrame(list(authors.items()), columns=['pmid', 'Author'])
Author

# get year for each article:
years = {}
for pmid in pmids:
    years[pmid] = fetch.article_by_pmid(pmid).year
Year = pd.DataFrame(list(years.items()), columns=['pmid', 'Year'])
Year

# get volume for each article:
volumes = {}
for pmid in pmids:
    volumes[pmid] = fetch.article_by_pmid(pmid).volume
Volume = pd.DataFrame(list(volumes.items()), columns=['pmid', 'Volume'])
Volume

# get issue for each article:
issues = {}
for pmid in pmids:
    issues[pmid] = fetch.article_by_pmid(pmid).issue
Issue = pd.DataFrame(list(issues.items()), columns=['pmid', 'Issue'])
Issue

# get journal for each article:
journals = {}
for pmid in pmids:
    journals[pmid] = fetch.article_by_pmid(pmid).journal
Journal = pd.DataFrame(list(journals.items()), columns=['pmid', 'Journal'])
Journal

# get citation for each article:
citations = {}
for pmid in pmids:
    citations[pmid] = fetch.article_by_pmid(pmid).citation
Citation = pd.DataFrame(list(citations.items()), columns=['pmid', 'Citation'])
Citation

links = {}
for pmid in pmids:
    links[pmid] = "https://pubmed.ncbi.nlm.nih.gov/" + pmid + "/"
Link = pd.DataFrame(list(links.items()), columns=['pmid', 'Link'])
Link

data_frames = [Title, Abstract, Author, Year, Volume, Issue, Journal, Citation, Link]
from functools import reduce

df_merged = reduce(lambda left, right: pd.merge(left, right, on=['pmid'],
                                                how='outer'), data_frames)
df_merged

df_merged.to_csv('pubmed_articles.csv')
