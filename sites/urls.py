from django.conf.urls import url
from . import views

app_name = 'sites'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add/?$', views.add, name='add'),
    url(r'^edit/?$', views.edit, name='edit'),
    url(r'^remove/?$', views.remove, name='remove'),
    url(r'^check/?$', views.check, name='check'),
    url(r'^api/check$', views.api_check, name='api_check'),
    url(r'^tos/?$', views.tos, name='tos'),
    url(r'^lang/?$', views.langlist, name='langlist'),
    url(r'^lang/(?P<language_code>[a-z]{2,5})/?$', views.lang, name='lang'),
    url(r'^lang/(?P<language_code>[a-z]{2,5})_(?P<country_code>[A-Z]{2,5})/?$', views.lang, name='lang'),
    url(r'^downloads/?$', views.downloads, name='downloads'),
    url(r'^downloads/urls.txt$', views.download_urls_txt, name='download_urls_txt'),
    url(r'^downloads/urls.json$', views.download_urls_json, name='download_urls_json'),
    url(r'^downloads/featured.json$', views.download_featured_json, name='download_featured_json'),
    url(r'^downloads/sites.json$', views.download_sites_json, name='download_sites_json'),
]
