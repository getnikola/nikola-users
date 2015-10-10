import itertools
from django.shortcuts import render
from django.core.mail import send_mail
from .models import Site, Language
from .checker import gencheck, CHECK_ERROR_NODATA
from .forms import AddForm, CheckForm

MENU = (
    ('/', 'Users Home', 'home'),
    ('/add/', 'Add', 'add'),
    ('/edit/', 'Edit', 'edit'),
    ('/remove/', 'Remove', 'remove'),
    ('/check/', 'Check sites', 'check'),
    ('/tos/', 'Terms of Service', 'tos'),
)


def index(request):
    """Index view."""
    featured = Site.objects.filter(featured=True).order_by('featured_order')
    other = Site.objects.filter(featured=False).order_by('?')  # random order
    count = Site.objects.count()

    all_sites = itertools.chain(featured, other)

    context = {
        'sites': all_sites,
        'count': count,
        'title': '{0} Sites'.format(count),
        'menu': MENU,
        'page': 'home'
    }

    return render(request, 'index.html', context)


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
            site.email = form.cleaned_data['email']
            site.description = form.cleaned_data['description']
            site.sourcelink = form.cleaned_data['sourcelink']
            site.publish_email = form.cleaned_data['publish_email']
            site.save()
            for lang in form.cleaned_data['languages']:
                try:
                    if '_' in lang:
                        lcode, ccode = lang.split('_')
                        site.languages.add(Language.objects.get(language_code=lcode, country_code=ccode))
                    else:
                        site.languages.add(Language.objects.get(language_code=lang))
                except Language.DoesNotExist:
                    context['reason'] = 'Language does not exist.'
                    return render(request, 'add-error.html', context)
            site.save()
            context['site'] = site

            send_mail("Nikola Users addition request for {0}".format(site.url),
                      "{0} <{1}> has requested addition of {2} <{3}> to the Nikola Users site.\nPlease visit the admin panel to accept or reject it:\nhttps://users.getnikola.com/admin/".format(
                          site.author, site.email, site.title, site.url),
                      'noreply@getnikola.com', ['users@getnikola.com'], fail_silently=False)

            return render(request, 'add-ack.html', context)
        else:
            context['reason'] = form.errors
            if 'tos' in form.errors:
                context['reason'] = 'tos'
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
        'data': [],
    }

    if request.method == 'POST':
        form = CheckForm(request.POST)
        if form.is_valid():
            context['data'] = gencheck(form.cleaned_data['url'])
            context['url'] = form.cleaned_data['url']
        else:
            context['data'] = CHECK_ERROR_NODATA

    return render(request, 'check.html', context)


def tos(request):
    """Terms of Service view."""
    context = {
        'menu': MENU,
        'title': 'Terms of Service',
        'page': 'tos',
    }

    return render(request, 'tos.html', context)
