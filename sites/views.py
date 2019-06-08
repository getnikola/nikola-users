import itertools

from django.shortcuts import render
from django.core.mail import send_mail
from django.utils.html import format_html
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required

from .models import Site, Language, BlacklistedURL
from .forms import AddForm

MENU = (
    ('/', 'Users Home', 'home'),
    ('/lang/', 'Languages', 'lang'),
    ('/add/', 'Add', 'add'),
    ('/edit/', 'Edit', 'edit'),
    ('/remove/', 'Remove', 'remove'),
    ('/check/', 'Check sites', 'check'),
    ('/tos/', 'Terms of Service', 'tos'),
    ('/downloads/', 'Downloads', 'downloads'),
)


def generic_index(request, title='{0} Sites', page='home', objects=None):
    """Generic index view."""
    featured = objects.filter(featured=True).order_by('featured_order')
    other = objects.filter(featured=False).order_by('?')  # random order
    count = objects.count()

    all_sites = itertools.chain(featured, other)

    context = {
        'sites': all_sites,
        'count': count,
        'title': title.format(count),
        'menu': MENU,
        'page': page
    }
    return render(request, 'index.html', context)


def index(request):
    """Language index view."""
    objects = Site.objects
    return generic_index(request, objects=objects)


def lang(request, **filters):
    lang = Language.objects.filter(**filters)
    if not lang:
        return HttpResponseNotFound()
    elif len(lang) == 1:
        lnames = str(lang[0])
        objects = lang[0].site_set
    else:
        lnames = ', '.join(str(_) for _ in lang)
        objects = Site.objects.filter(languages__language_code=filters['language_code'])
    return generic_index(request, title="{{0}} Sites in {0}".format(lnames), page='lang', objects=objects)


def langlist(request):
    group_members = list(Language.objects.filter(display_country=True).order_by('name'))
    groups = {}
    for l in group_members:
        if l.language_code in groups:
            groups[l.language_code].append(l)
        else:
            groups[l.language_code] = [l]

    groups_s = {}
    for lc, ll in groups.items():
        groups_s[lc] = format_html('<strong>{0}</strong>: {1}', lc, ', '.join(str(i) for i in ll))

    context = {
        'languages': Language.objects.order_by('name'),
        'language_groups': groups_s,
        'title': 'Languages',
        'menu': MENU,
        'page': 'lang'
    }
    return render(request, 'languages.html', context)


def add(request):
    """Add view."""
    context = {
        'menu': MENU,
        'title': 'Add',
        'page': 'add',
        'errors': [],
    }

    if request.method == 'POST':
        form = AddForm(request.POST)
        if form.is_valid():
            # Search for duplicates
            url = form.cleaned_data['url']
            try:
                Site.objects.get(url=url)
                context['reason'] = 'duplicate'
                return render(request, 'add-error.html', context)
            except Site.DoesNotExist:
                pass
            site = Site()
            site.title = form.cleaned_data['title']
            site.url = form.cleaned_data['url']
            site.author = form.cleaned_data['author']
            site.description = form.cleaned_data['description']
            site.sourcelink = form.cleaned_data['sourcelink']

            # Blacklisting
            blacklisted = False
            for bl in BlacklistedURL.objects.all():
                if (bl.exact and site.url == bl.url) or (not bl.exact and bl.url in site.url):
                    blacklisted = True
                    break

            if blacklisted:
                fake_languages = []
                for lang in form.cleaned_data['languages']:
                    try:
                        if '_' in lang:
                            lcode, ccode = lang.split('_')
                            fake_languages.append(Language.objects.get(language_code=lcode, country_code=ccode))
                        else:
                            fake_languages.append(Language.objects.get(language_code=lang))
                    except Language.DoesNotExist:
                        context['reason'] = 'Language does not exist.'
                        return render(request, 'add-error.html', context)

                context['site'] = site
                context['blacklisted'] = True
                context['fake_languages'] = fake_languages
                context['email_succeeded'] = True
                return render(request, 'add-ack.html', context)

            site.save()
            for lang in form.cleaned_data['languages']:
                try:
                    if '_' in lang:
                        lcode, ccode = lang.split('_')
                        site.languages.add(Language.objects.get(language_code=lcode, country_code=ccode))
                    else:
                        site.languages.add(Language.objects.get(language_code=lang))
                except Language.DoesNotExist:
                    site.delete()
                    context['reason'] = 'Language does not exist.'
                    return render(request, 'add-error.html', context)



            site.save()
            context['site'] = site

            try:
                send_mail(
                    "Nikola Users addition request for {0}".format(site.url),
                    '{0} has requested addition of "{1}" <{2}> to the Nikola Users site.\n'
                    'Please visit the admin panel to accept or reject it: https://users.getnikola.com/admin/'.format(
                        site.author, site.title, site.url),
                    'nikola-users@chriswarrick.com', ['nikola-users@chriswarrick.com'], fail_silently=False)
                context['email_succeeded'] = True
            except Exception:
                context['email_succeeded'] = False

            return render(request, 'add-ack.html', context)
        else:
            context['reason'] = form.errors
            if 'tos' in form.errors or 'ack_publishing' in form.errors:
                context['reason'] = 'tos_pub'
            return render(request, 'add-error.html', context)
    else:
        context['langs'] = Language.objects.order_by('name')
        return render(request, 'add.html', context)


def edit(request):
    """Edit view."""
    context = {
        'menu': MENU,
        'title': 'Edit',
        'page': 'edit'
    }
    return render(request, 'edit-remove.html', context)


def remove(request):
    """Remove view."""
    context = {
        'menu': MENU,
        'title': 'Remove',
        'page': 'remove'
    }
    return render(request, 'edit-remove.html', context)


def check(request):
    """Check view."""
    context = {
        'menu': MENU,
        'title': 'Check a Site',
        'page': 'check',
    }

    return render(request, 'check.html', context)


def api_check(request):
    """Check API."""
    return JsonResponse({"type": "error", "data": "This service has been disabled. Please see https://github.com/getnikola/nikola-users/blob/master/site_checker.py for a helper script."})


def tos(request):
    """Terms of Service view."""
    context = {
        'menu': MENU,
        'title': 'Terms of Service',
        'page': 'tos',
    }

    return render(request, 'tos.html', context)


def downloads(request):
    """Downloads page."""
    all_count = Site.objects.count()
    featured_count = Site.objects.filter(featured=True).count()
    context = {
        'menu': MENU,
        'title': 'Downloads',
        'page': 'downloads',
        'all_count': all_count,
        'featured_count': featured_count
    }

    return render(request, 'downloads.html', context)


def download_urls_txt(request):
    """Download URLs in text format."""
    urls = [s.url for s in Site.objects.filter(visible=True).order_by('pk')]
    urls.append('')  # trailing newline

    return HttpResponse('\n'.join(urls), content_type='text/plain')


def download_urls_json(request):
    """Download URLs in JSON format."""
    urls = {s.title: s.url for s in Site.objects.filter(visible=True).order_by('pk')}

    return JsonResponse(urls)


def download_json_handler(sites):
    data = []
    for site in sites:
        site_info = {
            'title': site.title,
            'url': site.url,
            'author': site.author,
            'description': site.description,
            'sourcelink': site.sourcelink,
            'languages': [lang.code for lang in site.languages.all()],
            'featured': site.featured
        }
        if site.featured:
            site_info['featured_order'] = site.featured_order
            site_info['featured_reason'] = site.featured_reason
        data.append(site_info)

    return JsonResponse(data, safe=False)


def download_featured_json(request):
    sites = Site.objects.filter(featured=True, visible=True).order_by('featured_order')
    return download_json_handler(sites)


@login_required
def download_sites_json(request):
    sites = Site.objects.filter(visible=True).order_by('pk')
    return download_json_handler(sites)
