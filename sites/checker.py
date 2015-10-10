import requests
from django.utils.html import format_html, mark_safe

CHECK_SUCCESS = mark_safe("""
<p class="text-success">
<i class="fa fa-check" style="font-size: 2em;"></i>
This is a Nikola site.</p>""")

CHECK_FAILURE = mark_safe("""
<p class="text-danger">
<i class="fa fa-times" style="font-size: 2em;"></i>
This is not a Nikola site.</p>""")

CHECK_UNKNOWN = """
<p class="text-warning">
<i class="fa fa-warning" style="font-size: 2em;"></i>
The check has failed. {0}</p>"""

CHECK_ERROR_NODATA = [mark_safe("""
<p class="text-warning">
<i class="fa fa-warning" style="font-size: 2em;"></i>
No URL provided or the form is invalid.</p>""")]


def gencheck(homeurl):
    yield format_html('<p>Checking site: <strong>{0}</strong>.</p>', homeurl)
    burl = homeurl.split('index.html')[0]
    if not burl.endswith('/'):
        burl += '/'
    if homeurl != burl:
        yield format_html('<p>Base determined as <strong>{0}</strong>.</p>', burl)
    rssurl = burl + 'rss.xml'
    try:
        r = requests.get(rssurl)
        nsite = False
        patterns = [b'<generator>https://getnikola.com/</generator>',         # v7.6.1
                    b'<generator>http://getnikola.com/</generator>',          # v7.0.0
                    b'<generator>Nikola <http://getnikola.com/></generator>', # v6.3.0
                    b'<generator>nikola</generator>']                         # v6.2.1
        for i in patterns:
            if i in r.content:
                nsite = True

        if nsite:
            yield CHECK_SUCCESS
        elif r.status_code not in [200, 404]:
            yield format_html(CHECK_UNKNOWN, 'HTTP Error {0}.'.format(r.status_code))
        else:
            yield CHECK_FAILURE
    except NameError as e:
        yield format_html(CHECK_UNKNOWN, 'An unhandled exception occurred: ' + str(e))
