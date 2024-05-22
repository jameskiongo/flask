from decimal import Decimal
from numbers import Number

from jinja2 import Markup


def format_currency(value):
    if not isinstance(value, (Number, Decimal)):
        raise TypeError("Value must be Number.")
    if value < 0:
        return Markup('<span style="color:red">- </span>' + format_currency(-value))
    return "${:,.2f}".format(value)
