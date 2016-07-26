from django import forms
from .models import Language

def make_choices():
    return [(l.code, l.name) for l in Language.objects.all().order_by('name')]

class AddForm(forms.Form):
    title = forms.CharField(label="Title", max_length=100)
    url = forms.URLField(label="URL", max_length=512)
    author = forms.CharField(label="Author", max_length=100)
    email = forms.EmailField(label="E-mail address", max_length=100)
    description = forms.CharField(label="Description", max_length=250)
    sourcelink = forms.URLField(label="Site source", max_length=512, required=False)
    languages = forms.MultipleChoiceField(label="Languages", required=False, choices=make_choices)
    tos = forms.BooleanField(label="Accept TOS")
    publish_email = forms.BooleanField(label="Publish e-mail", required=False)


class CheckForm(forms.Form):
    url = forms.URLField(label="URL to check", max_length=256)
