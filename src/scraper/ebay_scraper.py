from bs4 import BeautifulSoup

import requests
import json

def scrape_site():

    url = 'http://www.ebay.com/itm/Nikon-AF-S-DX-NIKKOR-55-200mm-f-4-5-6G-ED-VR-II-Lens-Factory-Refurbished-/311498162380?_trkparms=%26rpp_cid%3D5702b40de4b0826387589b2e%26rpp_icid%3D5702cf3fe4b079ecf2fa287f'

    r  = requests.get(url)

    data = r.text

    soup = BeautifulSoup(data, 'html.parser')
    json_data = {}

    titleEl = soup.find("h1", {"id": "itemTitle"})
    if not(titleEl is None):
        json_data['title'] = titleEl.text.strip('Details about')

    priceEl = soup.find("span", {"id": "mm-saleDscPrc"})
    if not (priceEl is None):
        json_data['price'] = (priceEl.text).strip()

    shippingEl = soup.find("span", {"id": "fshippingCost"})
    if not (shippingEl is None):
        json_data['shippingCost'] = (shippingEl.text).strip()

    shippingToEl = soup.find("div", {"class": "sh-sLoc"})
    if not (shippingToEl is None):
        json_data['shippingTo'] = (shippingToEl.text).strip()


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


    product_data = json.dumps(json_data)
    # print(product_data)

    return product_data





