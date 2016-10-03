from django.conf.urls import include, url

urlpatterns = [
    url(r'^submissions/(?P<pages>\d+)$',
        'news_crawler.api.get_submissions', name='get_submissions'),

    # url(r'^posts/(user)$', '', name=''),
    #
    # url(r'^submitters/top$', '', name=''),
    #
    # url(r'^commenters/top$', '', name=''),
    #
    # url(r'^users/most_active$', '', name=''),

]
