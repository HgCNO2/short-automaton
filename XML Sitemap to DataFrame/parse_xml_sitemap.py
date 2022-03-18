# Import Modules
import pandas as pd
from bs4 import BeautifulSoup
import requests
from lxml.etree import XMLSyntaxError


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
    soup = BeautifulSoup(resp.content, 'xml')
    if soup.select('sitemapindex'):
        sitemaps = pd.read_xml(resp.content)
        for each_sitemap in sitemaps['loc'].tolist():
            resp = requests.get(each_sitemap, **kwargs)
            if resp.ok:
                urls = pd.concat([urls, pd.read_xml(resp.content)])
            else:
                print(f'Unable to fetch {each_sitemap}. Request returned HTTP Response {resp.status_code}.')
    else:
        urls = pd.read_xml(resp.content)
    return urls


if __name__ == '__main__':
    # TODO Debug 403: Forbidden when using Pandas
    test_df = parse_sitemap('https://www.screamingfrog.co.uk/sitemap.xml')
    test_df = extract_urls('https://www.screamingfrog.co.uk/sitemap.xml', True)
    # test_df = extract_urls('https://www.condo-world.com/sitemap.xml', False)
