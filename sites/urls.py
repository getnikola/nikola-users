from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add/?$', views.add, name='add'),
    url(r'^edit/?$', views.edit, name='edit'),
    url(r'^remove/?$', views.remove, name='remove'),
    url(r'^check/?$', views.check, name='check'),
    url(r'^tos/?$', views.tos, name='tos'),
    url(r'^lang/?$', views.langlist, name='langlist'),
    url(r'^lang/(?P<language_code>[a-z]{2,5})/?$', views.lang, name='lang'),
    url(r'^lang/(?P<language_code>[a-z]{2,5})_(?P<country_code>[A-Z]{2,5})/?$', views.lang, name='lang'),
]
