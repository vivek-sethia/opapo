from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

import requests
import json

def scrape_ebay_site_external(upc) :
    browser = webdriver.Firefox()
    browser.get('http://www.ebay.com')

    element = browser.find_element_by_name("_nkw")
    element.send_keys(upc)
    browser.find_element_by_css_selector('.gh-td .gh-spr').click()
    html_source = browser.page_source

    browser.quit()

    soup = BeautifulSoup(html_source, 'html.parser')

    resultsEl = soup.select('a[class="vip"]')

    if not (resultsEl is None):
        url = resultsEl[0].attrs["href"]
        ebay_data = scrape_ebay_site(url)
        return ebay_data

def scrape_ebay_site(url):

    #url = 'http://www.ebay.com/itm/Nikon-AF-S-DX-NIKKOR-55-200mm-f-4-5-6G-ED-VR-II-Lens-Factory-Refurbished-/311498162380?_trkparms=%26rpp_cid%3D5702b40de4b0826387589b2e%26rpp_icid%3D5702cf3fe4b079ecf2fa287f'

    r  = requests.get(url)

    data = r.text

    soup = BeautifulSoup(data, 'html.parser')
    json_data = {}

    titleEl = soup.find("h1", {"id": "itemTitle"})
    if not(titleEl is None):
        json_data['title'] = titleEl.text.strip('Details about')

    priceEl = soup.find("span", {"id": "mm-saleDscPrc"}) or soup.find("span", {"id": "prcIsum"})
    if not (priceEl is None):
        json_data['price'] = (priceEl.text).strip()

    savingsEl = soup.find("span", {"id": "youSaveSTP"})
    if not (savingsEl is None):
        json_data['savings'] = (savingsEl.text).strip()

    soldQuantityEl = soup.find("span", {"class": "w2b-sgl"})
    if not (soldQuantityEl is None):
        json_data['sold_quantity'] = (soldQuantityEl.text).strip().rstrip(" sold")

    shippingEl = soup.find("span", {"id": "fshippingCost"})
    if not (shippingEl is None):
        json_data['shippingCost'] = (shippingEl.text).strip()

    shippingToEl = soup.find("div", {"class": "sh-sLoc"})
    if not (shippingToEl is None):
        json_data['shippingTo'] = (shippingToEl.text).strip().lstrip("Shipping to: ")


    imageEl = soup.find("img", {"id": "icImg"})
    if not(imageEl is None):
        json_data['image'] = imageEl.attrs["src"]


    brandEl = soup.find("h2", {"itemprop": "brand"})
    if not(brandEl is None):
        json_data['brand'] = brandEl.text

    merchantEl = soup.find("span", {"class": "mbg-nw"})
    if not (merchantEl is None):
        json_data['merchant'] = merchantEl.text

    savingsEl = soup.find("div", {"id": "mm-saleAmtSavedPrc"})
    if not (savingsEl is None):
        json_data['savings'] = (savingsEl.text).strip()

    availabilityEl = soup.find("span", {"id": "qtySubTxt"})
    if not(availabilityEl is None):
            json_data['availability'] = (availabilityEl.text).strip()

    returnInEl = soup.find("span", {"id": "vi-ret-accrd-txt"})
    if not (returnInEl is None):
        json_data['returnIn'] = (returnInEl.text).strip()

    sellerfbEl = soup.find("div", {"id": "si-fb"})
    if not (sellerfbEl is None):
        json_data['sellerFeedback'] = (sellerfbEl.text).strip()

    linktoBuyEl = soup.find("a", {"id": "binBtn_btn"})
    if not (linktoBuyEl is None):
        json_data['linkToBuy'] = (linktoBuyEl.text).strip()

    paymentElRow = soup.find("div", {"id": "payDet1"})
    if not (paymentElRow is None):
        json_data['payment'] = {}
        index = 1

        for paymentEl in paymentElRow.find_all("img"):
            if not (paymentEl is None):
                json_data['payment'][index] = paymentEl.attrs['alt'];
                index += 1

    ratingEl = soup.find("a", {"id": "_rvwlnk"})
    if not (ratingEl is None):
        json_data['rating'] = (ratingEl.text).strip()

    reviewsElBlock = soup.find("div", {"class": "reviews"})
    if not(reviewsElBlock is None):
        json_data['reviews'] = {}
        index = 1

        for reviewsEl in reviewsElBlock.find_all("div", {"class": "ebay-review-section"}):
            if not(reviewsEl is None):

                json_data['reviews'][index] = {}
                reviewedByEl = reviewsEl.find("a", {"itemprop": "author"})
                if not(reviewedByEl is None):
                    json_data['reviews'][index]['reviewed_by'] = reviewedByEl.text.strip()

                reviewRatingEl = reviewsEl.find("div", {"class": "ebay-star-rating"})
                if not(reviewRatingEl is None):
                    json_data['reviews'][index]['rating'] = reviewRatingEl.attrs["title"].strip()

                reviewNameEl = reviewsEl.find("p", {"itemprop": "name"})
                if not(reviewNameEl is None):
                    json_data['reviews'][index]['title'] = reviewNameEl.text.strip()

                reviewDescriptionEl = reviewsEl.find("p", {"itemprop": "reviewBody"})
                if not(reviewDescriptionEl is None):
                    json_data['reviews'][index]['description'] = reviewDescriptionEl.text.strip()

                reviewedOnEl = reviewsEl.find("span", {"itemprop": "datePublished"})
                if not(reviewedOnEl is None):
                    json_data['reviews'][index]['reviewed_on'] = reviewedOnEl.text.strip()

                reviewAttributesElBlock = reviewsEl.find("p", {"class": "review-attr"})
                if not(reviewAttributesElBlock is None):
                    attributeIndex = 0
                    for reviewAttributesEl in reviewAttributesElBlock.find_all("span", {"class": "rvw-attr"}):
                        if not(reviewAttributesEl is None):

                            reviewValueEl = reviewAttributesElBlock.select("span.rvw-val")[attributeIndex]
                            if not(reviewValueEl is None):

                                json_data['reviews'][index][reviewAttributesEl.text.strip()] = reviewValueEl.text.strip()
                                attributeIndex += 1

                    index += 1

    data = {}
    data['scraped_data'] = json_data
    # print(product_data)

    return data





