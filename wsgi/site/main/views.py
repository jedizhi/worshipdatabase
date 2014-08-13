from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import MySQLdb, os, string

# Create your views here.
def home(request):
    context = {
        'title': 'Home',
        'style': 'home.css'
    }
    return render(request, 'main/index.html', context)

def about(request):
    context = {'title': 'About'}
    return render(request, 'main/about.html', context)

def search(request):
    params = request.GET
    if len(params) == 0:
        return HttpResponseRedirect(reverse('home'))
    query = params['query']
    result = doSearch(query)

    context = {
        'title': 'Search',
        'style': 'search.css',
        'query': query,
        'pages': result['pages'],
        'songs': result['songs']
    }
    return render(request, 'main/search.html', context)

def doSearch(query):
    query = string.replace(query.lower(), '\'', '\\\'')

    # search pages
    pages = []
    for page, link in {
        ('Home', 'home'),
        ('About', 'about'),
        ('Database', 'database:index'),
        ('Contact', 'contact:index'),
        ('Transpose', 'transpose:index'),
        ('Transposition', 'transpose:index')
    }:
        if page.lower() in query:
            pages.append((page, reverse(link)))

    # search songs
    if 'OPENSHIFT' in os.environ:
        conn = MySQLdb.connect(
            host=os.environ['OPENSHIFT_MYSQL_DB_HOST'],
            user=os.environ['OPENSHIFT_MYSQL_DB_USERNAME'],
            passwd=os.environ['OPENSHIFT_MYSQL_DB_PASSWORD'],
            db=os.environ['OPENSHIFT_APP_NAME'],
            port=int(os.environ['OPENSHIFT_MYSQL_DB_PORT'])
        )
    else:
        conn = MySQLdb.connect(user='root', db='worshipdb')

    c = conn.cursor()
    c.execute("SELECT title FROM database_song WHERE MATCH \
        (title, artist, themes, lyrics) AGAINST (\'" + query + "\')")
    songs = [(song[0], reverse('database:detail', args=[song[0].replace(" ", "-")]\
        )) for song in c.fetchall()]
    c.close()
    conn.close()

    return {
        'pages': pages,
        'songs': songs
    }