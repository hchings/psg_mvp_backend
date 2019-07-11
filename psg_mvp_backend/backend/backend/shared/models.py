from djongo import models
from django import forms


class SimpleString(models.Model):
    """
    # TODO: tmp workaround because Djongo project does not support non-document simple array.
    # TODO: related issue:
    Abstract model representing for being used as an ArrayField as in postgre.
    """
    class Meta:
        abstract = True

    value = models.CharField(max_length=30, blank=True)


class SimpleStringForm(forms.ModelForm):
    """
    Customize form for ArrayModelField from djongo bcz
    the self-generated Form has all fields set to required.
    """
    class Meta:
        model = SimpleString
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(SimpleString, self).__init__(*args, **kwargs)
        # all fields are not required except for branch_name
        for key, _ in self.fields.items():
            self.fields[key].required = False
