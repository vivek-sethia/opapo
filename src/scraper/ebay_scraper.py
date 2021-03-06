from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from vaderSentiment.vaderSentiment import sentiment
from watson_developer_cloud import ToneAnalyzerV3


import requests
import json
import re


def get_ebay_page(id):

    browser = webdriver.PhantomJS()
    browser.get('http://www.ebay.com')

    element = browser.find_element_by_name("_nkw")
    element.send_keys(id)
    browser.find_element_by_css_selector('.gh-td .gh-spr').click()
    html_source = browser.page_source

    browser.quit()

    return html_source


def scrape_ebay_site_external(upc, name, config):
    data = {
        'scraped_data': ''
    }
    if upc == '':
        return data

    html_source = get_ebay_page(upc)
    soup = BeautifulSoup(html_source, 'html.parser')

    results_el = soup.select('a[class="vip"]')

    if results_el and not (results_el is None):
        url = results_el[0].attrs["href"]
        ebay_data = scrape_ebay_site(url, config)
        ebay_data['scraped_data']['product_link'] = url
        return ebay_data
    else:
        name = re.sub('\(.*\)', '', name)
        html_source = get_ebay_page(name)
        soup = BeautifulSoup(html_source, 'html.parser')

        results_el = soup.select('a[class="vip"]')

        if results_el and not (results_el is None):
            url = results_el[0].attrs["href"]
            ebay_data = scrape_ebay_site(url, config)
            ebay_data['scraped_data']['product_link'] = url
            return ebay_data


def scrape_ebay_site(url, config):

    # url = 'http://www.ebay.com/itm/Nikon-AF-S-DX-NIKKOR-55-200mm-f-4-5-6G-ED-VR-II-Lens-Factory-Refurbished-/
    # 311498162380?_trkparms=%26rpp_cid%3D5702b40de4b0826387589b2e%26rpp_icid%3D5702cf3fe4b079ecf2fa287f'

    r = requests.get(url)

    data = r.text

    soup = BeautifulSoup(data, 'html.parser')
    json_data = {}

    title_el = soup.find("h1", {"id": "itemTitle"})
    if not(title_el is None):
        json_data['title'] = title_el.text.strip('Details about')

    price_el = soup.find("span", {"id": "mm-saleDscPrc"}) or soup.find("span", {"id": "prcIsum"}) or \
        soup.find("span", {"id": "prcIsum_bidPrice"})
    if not (price_el is None):
        json_data['price'] = price_el.text.strip().lstrip('US ')

    savings_el = soup.find("span", {"id": "youSaveSTP"})
    if not (savings_el is None):
        json_data['savings'] = savings_el.text.strip()

    sold_quantity_el = soup.find("span", {"class": "w2b-sgl"})
    if not (sold_quantity_el is None):
        json_data['sold_quantity'] = sold_quantity_el.text.strip().rstrip(" sold")

    shipping_el = soup.find("span", {"id": "fshippingCost"})
    if not (shipping_el is None):
        json_data['shippingCost'] = shipping_el.text.strip()

    shipping_to_el = soup.find("div", {"class": "sh-sLoc"})
    if not (shipping_to_el is None):
        json_data['shippingTo'] = shipping_to_el.text.strip().lstrip("Shipping to: ")

    image_el = soup.find("img", {"id": "icImg"})
    if not(image_el is None):
        json_data['image'] = image_el.attrs["src"]

    brand_el = soup.find("h2", {"itemprop": "brand"})
    if not(brand_el is None):
        json_data['brand'] = brand_el.text

    json_data['merchant'] = {}

    merchant_el = soup.find("span", {"class": "mbg-nw"})
    if not (merchant_el is None):
        json_data['merchant']['name'] = merchant_el.text.title()

    merchant_sold_quantity = soup.find("span", {"class": "mbg-l"})
    if not (merchant_sold_quantity is None):
        json_data['merchant']['sold_quantity'] = merchant_sold_quantity.text.strip().lstrip('(').rstrip(')')

    merchant_feedback = soup.find("div", {"id": "si-fb"})
    if not (merchant_feedback is None):
        json_data['merchant']['feedback'] = merchant_feedback.text

    savings_el = soup.find("div", {"id": "mm-saleAmtSavedPrc"})
    if not (savings_el is None):
        json_data['savings'] = savings_el.text.strip()

    availability_el = soup.find("span", {"id": "qtySubTxt"})
    if not(availability_el is None):
            json_data['availability'] = availability_el.text.strip()

    return_in_el = soup.find("span", {"id": "vi-ret-accrd-txt"})
    if not (return_in_el is None):
        json_data['returnIn'] = return_in_el.text.strip()

    seller_fb_el = soup.find("div", {"id": "si-fb"})
    if not (seller_fb_el is None):
        json_data['sellerFeedback'] = seller_fb_el.text.strip()

    link_to_buy_el = soup.find("a", {"id": "binBtn_btn"})
    if not (link_to_buy_el is None):
        json_data['linkToBuy'] = link_to_buy_el.text.strip()

    payment_el_row = soup.find("div", {"id": "payDet1"})
    if not (payment_el_row is None):
        json_data['payment'] = {}
        index = 1

        for paymentEl in payment_el_row.find_all("img"):
            if not (paymentEl is None):
                json_data['payment'][index] = paymentEl.attrs['alt']
                index += 1

    json_data['rating'] = {}

    rating_el = soup.find("span", {"class": "num-of-rewiews"})
    if not (rating_el is None):
        review_count_el = rating_el.find("a")
        if not(review_count_el is None):
            json_data['rating']['review_count'] = review_count_el.text.strip().rstrip(' rating').rstrip('s')

    if json_data['rating'].get('review_count') is None:
        rating_el = soup.find("a", {"id": "_rvwlnk"})
        if not (rating_el is None):
            json_data['rating']['review_count'] = int(rating_el.text.strip().rstrip('s').rstrip(' rating'))

    average_rating_el = soup.find("span", {"class": "review--start--rating"}) or \
        soup.find("span", {"class": "ebay-review-start-rating"})
    if not(average_rating_el is None):
        json_data['rating']['average'] = average_rating_el.text.strip()

    review_summary_el = soup.find('ul', {'class': 'ebay-review-list'})
    if not(review_summary_el is None):
        json_data['rating']['stats'] = {}

        for review_row_el in review_summary_el.find_all('li', {'class': 'ebay-review-item'}):
            if not(review_row_el is None):
                review_name_el = review_row_el.find("p", {"class": "ebay-review-item-stars"})
                review_rating_el = review_row_el.find("div", {"class": "ebay-review-item-r"}).find("span")
                if review_name_el and review_rating_el:
                    json_data['rating']['stats'][review_name_el.text + ' star'] = review_rating_el.text

    reviews_el_block = soup.find("div", {"class": "reviews"})
    if not(reviews_el_block is None):
        json_data['reviews'] = {}
        index = 1
        overall_sentiment = 0
        all_reviews = ''

        for reviewsEl in reviews_el_block.find_all("div", {"class": "ebay-review-section"}):
            if not(reviewsEl is None):

                json_data['reviews'][index] = {}
                reviewed_by_el = reviewsEl.find("a", {"itemprop": "author"})
                if not(reviewed_by_el is None):
                    json_data['reviews'][index]['reviewed_by'] = reviewed_by_el.text.strip()

                review_rating_el = reviewsEl.find("div", {"class": "ebay-star-rating"})
                if not(review_rating_el is None):
                    json_data['reviews'][index]['review_rating'] = (review_rating_el.attrs.get("title") or review_rating_el.attrs.get("aria-label")).strip()

                review_name_el = reviewsEl.find("p", {"itemprop": "name"})
                if not(review_name_el is None):
                    json_data['reviews'][index]['title'] = review_name_el.text.strip()

                review_description_el = reviewsEl.find("p", {"itemprop": "reviewBody"})
                if not(review_description_el is None):

                    reviews_text = review_description_el.text.strip()
                    json_data['reviews'][index]['text'] = reviews_text

                    review_sentiment = sentiment(reviews_text)
                    all_reviews += reviews_text
                    overall_sentiment += review_sentiment['compound']

                reviewed_on_el = reviewsEl.find("span", {"itemprop": "datePublished"})
                if not(reviewed_on_el is None):
                    json_data['reviews'][index]['reviewed_on'] = reviewed_on_el.text.strip()

                review_attributes_el_block = reviewsEl.find("p", {"class": "review-attr"})
                if not(review_attributes_el_block is None):
                    attribute_index = 0
                    for reviewAttributesEl in review_attributes_el_block.find_all("span", {"class": "rvw-attr"}):
                        if not(reviewAttributesEl is None):

                            review_value_el = review_attributes_el_block.select("span.rvw-val")[attribute_index]
                            if not(review_value_el is None):

                                json_data['reviews'][index][reviewAttributesEl.text.strip()] = \
                                    review_value_el.text.strip()
                                attribute_index += 1

                    index += 1

        if all_reviews != '':
            json_data['tones'] = get_tone(all_reviews, config)
            json_data['overall_sentiment'] = round(overall_sentiment/index, 2)

    data = {
        'scraped_data': json_data
    }
    # print(product_data)

    return data


def get_tone(text, config):

    tones = {}
    tone_analyzer = ToneAnalyzerV3(
        username=config['WDC_TA_USER_NAME'],
        password=config['WDC_TA_PASSWORD'],
        version=config['WDC_TA_VERSION'])

    result_tone = tone_analyzer.tone(text=text)
    if result_tone is not None:
        tones = {}
        for category in result_tone['document_tone']['tone_categories']:
            category_name = category['category_id'].replace('_tone', '')
            tones[category_name] = {
                'tone_names': [],
                'scores': []
            }
            for tone in category['tones']:
                tones[category_name]['tone_names'].append(tone['tone_name'])
                tones[category_name]['scores'].append(tone['score'])

    return tones
