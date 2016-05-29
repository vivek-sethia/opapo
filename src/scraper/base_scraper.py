from amazon_scraper import scrape_amazon_site
from ebay_scraper import scrape_ebay_site_external
import json

def scrape_site(public_key, private_key, associate_tag, url) :
    data = {}

    amazon_data = scrape_amazon_site(public_key, private_key, associate_tag, url);
    data['amazon'] = amazon_data['scraped_data']

    ebay_data = scrape_ebay_site_external(amazon_data['id'])
    data['ebay'] = ebay_data['scraped_data']

    product_data = json.dumps(data, sort_keys=True)
    return product_data
