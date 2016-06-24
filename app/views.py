from flask import render_template, flash, redirect, Flask, Response
from app import app
from .forms import SearchForm
from src.scraper.base_scraper import scrape_site
import json


@app.route('/')
def home():
    return redirect('/search')


@app.route('/data.json')
def get_data():
    with open('app/data.json') as json_data:
        data = json.load(json_data)
        json_data.close()

        product_data = json.dumps(data, sort_keys=True)
        resp = Response(product_data, status=200, mimetype='application/json')
        return resp


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        # flash('Search requested for Product="%s"' % (str(form.product.data)))
        scrape_site(app.config['PUBLIC_KEY'], app.config['PRIVATE_KEY'], app.config['ASSOCIATE_TAG'],
                    str(form.product_format.data), str(form.product.data))

        return render_template('result.html')

    return render_template('search.html', title='Product Search', form=form)
