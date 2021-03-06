from django import forms
from .models import Language

def make_choices():
    return [(l.code, l.name) for l in Language.objects.all().order_by('name')]


class AddForm(forms.Form):
    title = forms.CharField(label="Title", max_length=100)
    url = forms.URLField(label="URL", max_length=512)
    author = forms.CharField(label="Author", max_length=100)
    description = forms.CharField(label="Description", max_length=250)
    sourcelink = forms.URLField(label="Site source", max_length=512, required=False)
    languages = forms.MultipleChoiceField(label="Languages", required=True, choices=make_choices)
    tos = forms.BooleanField(label="Accept TOS", required=True)
    ack_publishing = forms.BooleanField(label="Accept publishing", required=True)
