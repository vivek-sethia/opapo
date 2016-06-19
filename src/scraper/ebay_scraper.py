from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

import requests
import json


def scrape_ebay_site_external(upc):
    data = {
        'scraped_data': ''
    }
    if upc == '':
        return data

    browser = webdriver.PhantomJS()
    browser.get('http://www.ebay.com')

    element = browser.find_element_by_name("_nkw")
    element.send_keys(upc)
    browser.find_element_by_css_selector('.gh-td .gh-spr').click()
    html_source = browser.page_source

    browser.quit()

    soup = BeautifulSoup(html_source, 'html.parser')

    results_el = soup.select('a[class="vip"]')

    if not (results_el is None):
        url = results_el[0].attrs["href"]
        ebay_data = scrape_ebay_site(url)
        return ebay_data


def scrape_ebay_site(url):

    # url = 'http://www.ebay.com/itm/Nikon-AF-S-DX-NIKKOR-55-200mm-f-4-5-6G-ED-VR-II-Lens-Factory-Refurbished-/
    # 311498162380?_trkparms=%26rpp_cid%3D5702b40de4b0826387589b2e%26rpp_icid%3D5702cf3fe4b079ecf2fa287f'

    r = requests.get(url)

    data = r.text

    soup = BeautifulSoup(data, 'html.parser')
    json_data = {}

    title_el = soup.find("h1", {"id": "itemTitle"})
    if not(title_el is None):
        json_data['title'] = title_el.text.strip('Details about')

    price_el = soup.find("span", {"id": "mm-saleDscPrc"}) or soup.find("span", {"id": "prcIsum"})
    if not (price_el is None):
        json_data['price'] = price_el.text.strip()

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

    merchant_el = soup.find("span", {"class": "mbg-nw"})
    if not (merchant_el is None):
        json_data['merchant'] = merchant_el.text

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

    rating_el = soup.find("a", {"id": "_rvwlnk"})
    if not (rating_el is None):
        json_data['rating'] = rating_el.text.strip()

    reviews_el_block = soup.find("div", {"class": "reviews"})
    if not(reviews_el_block is None):
        json_data['reviews'] = {}
        index = 1

        for reviewsEl in reviews_el_block.find_all("div", {"class": "ebay-review-section"}):
            if not(reviewsEl is None):

                json_data['reviews'][index] = {}
                reviewed_by_el = reviewsEl.find("a", {"itemprop": "author"})
                if not(reviewed_by_el is None):
                    json_data['reviews'][index]['reviewed_by'] = reviewed_by_el.text.strip()

                review_rating_el = reviewsEl.find("div", {"class": "ebay-star-rating"})
                if not(review_rating_el is None):
                    json_data['reviews'][index]['rating'] = review_rating_el.attrs["title"].strip()

                review_name_el = reviewsEl.find("p", {"itemprop": "name"})
                if not(review_name_el is None):
                    json_data['reviews'][index]['title'] = review_name_el.text.strip()

                review_description_el = reviewsEl.find("p", {"itemprop": "reviewBody"})
                if not(review_description_el is None):
                    json_data['reviews'][index]['description'] = review_description_el.text.strip()

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

    data = {
        'scraped_data': json_data
    }
    # print(product_data)

    return data
