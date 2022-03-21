# Import Modules
import pandas as pd
from bs4 import BeautifulSoup
import requests
from lxml.etree import XMLSyntaxError
import gzip


def extract_urls(sitemap, index=False):
    urls = pd.DataFrame()
    if index:
        sitemap_index_df = pd.read_xml(sitemap)
        for xml_sitemap in sitemap_index_df['loc'].tolist():
            try:
                urls = pd.concat([urls, pd.read_xml(xml_sitemap)])
            except XMLSyntaxError:
                print(xml_sitemap, 'unreadable.')
            except UnicodeEncodeError:
                print(xml_sitemap, 'unicode error.')
    else:
        urls = pd.read_xml(sitemap)
    return urls


def parse_sitemap(sitemap, **kwargs):
    urls = pd.DataFrame()
    resp = requests.get(sitemap, **kwargs)
    if not resp.ok:
        print(f'Unable to fetch sitemap. Request returned HTTP Response {resp.status_code}. Please check your input.')
        return None
    if resp.headers['Content-Type'] == 'application/x-gzip':
        content = gzip.decompress(resp.content)
    else:
        content = resp.content
    soup = BeautifulSoup(content, 'xml')
    if soup.select('sitemapindex'):
        sitemaps = pd.read_xml(content)
        for each_sitemap in sitemaps['loc'].tolist():
            resp = requests.get(each_sitemap, **kwargs)
            if resp.ok:
                if resp.headers['Content-Type'] == 'application/x-gzip':
                    content = gzip.decompress(resp.content)
                else:
                    content = resp.content
                urls = pd.concat([urls, pd.read_xml(content)])
            else:
                print(f'Unable to fetch {each_sitemap}. Request returned HTTP Response {resp.status_code}.')
    else:
        urls = pd.read_xml(content)
    return urls


if __name__ == '__main__':
    test_pandas = extract_urls('https://schema.org/docs/sitemap.xml')
    test_df = parse_sitemap('https://www.screamingfrog.co.uk/sitemap.xml')
    test_gzip = parse_sitemap('https://www.dictionary.com/dictionary-sitemap/sitemap.xml')
