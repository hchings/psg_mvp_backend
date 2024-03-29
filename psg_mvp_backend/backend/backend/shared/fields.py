"""
Custom field for Djongo abstract model.

reason: Djongo's abstract model does not support DecimalField.
* See open issue here: https://github.com/nesdis/djongo/issues/82

"""

import decimal
import coloredlogs, logging
from bson.decimal128 import Decimal128
from djongo.models import DecimalField

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


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


def embedded_model_method(obj,
                          model,
                          field_name,
                          included_fields=[],
                          value_mapping={}):
    """
    Serializer field for EmbeddedModelField from djongo.
    https://github.com/nesdis/djongo/issues/115.


    :param(model instance) obj:
    :param(model class) model:
    :param(str) field_name:
    :param(list of str) included_fields: if set, the return json
        will only contain those explicitly specified fields
    :param(dict): mapping to transform value. {ori_value: transformed_value}
    :return:
    """

    field_object = model._meta.get_field(field_name)
    field_value = field_object.value_from_object(obj)

    try:
        if type(field_value) == list:
            embedded_list = []
            for item in field_value:
                embedded_dict = item.__dict__
                for key in list(embedded_dict.keys()):
                    if key.startswith('_') or (len(included_fields) > 0 and key not in included_fields):
                        embedded_dict.pop(key)
                        continue
                    if value_mapping:
                        # transform dict value
                        embedded_dict[key] = value_mapping.get(embedded_dict[key], embedded_dict[key])
                embedded_list.append(embedded_dict)
            return_data = embedded_list
        else:
            embedded_dict = field_value.__dict__
            for key in list(embedded_dict.keys()):
                if key.startswith('_') or (len(included_fields) > 0 and key not in included_fields):
                    embedded_dict.pop(key)
            return_data = embedded_dict
        return return_data
    except AttributeError as e:
        # field name non exist
        logger.error("Error: " + str(e))
        return []
