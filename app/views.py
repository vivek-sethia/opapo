from flask import render_template, flash, redirect, Flask, Response
from app import app
from .forms import SearchForm
from src.scraper.amazon_scraper import scrape_site


@app.route('/')
def home():
    return redirect('/search')


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        # flash('Search requested for Product="%s"' % (str(form.product.data)))
        data = scrape_site(str(form.product.data))
        resp = Response(data, status=200, mimetype='application/json')
        return resp

    return render_template('search.html', title='Product Search', form=form)
