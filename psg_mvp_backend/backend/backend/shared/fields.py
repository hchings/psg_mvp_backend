"""
Custom field for Djongo abstract model.

reason: Djongo's abstract model does not support DecimalField.
* See open issue here: https://github.com/nesdis/djongo/issues/82

"""

import decimal
from bson.decimal128 import Decimal128
from djongo.models import DecimalField


class MongoDecimalField(DecimalField):
    def to_python(self, value):
        if not value:
            # TODO: should have better way to represent None/blank
            value = 0
        elif isinstance(value, Decimal128):
            value = self.format_number(value.to_decimal())
        return super().to_python(value)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        return Decimal128(value)

    def format_number(self, value, max_digits=9, decimal_places=6):
        """
        Format a number into a string with the requisite number of digits and
        decimal places.
        """
        if value is None:
            return None
        context = decimal.getcontext().copy()
        if max_digits is not None:
            context.prec = max_digits
        if decimal_places is not None:
            value = value.quantize(decimal.Decimal(1).scaleb(-decimal_places), context=context)
        else:
            context.traps[decimal.Rounded] = 1
            value = context.create_decimal(value)
        return "{:f}".format(value)
