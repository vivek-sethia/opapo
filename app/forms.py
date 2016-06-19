from flask.ext.wtf import Form
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired


class SearchForm(Form):
    product_format = SelectField(
        'Product Code Format',
        choices=[('url', 'Product URL'), ('asin', 'Amazon Product Code'), ('upc', 'Universal Product Code')],
        validators=[DataRequired()]
    )
    product = StringField('product', validators=[DataRequired()])
