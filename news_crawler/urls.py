from django.conf.urls import include, url

urlpatterns = [
    url(r'^submissions/(?P<pages>\d+)$',
        'news_crawler.api.get_submissions', name='get_submissions'),

    url(r'^submissions/articles/top10$',
        'news_crawler.api.get_top10_articles', name='get_top10_articles'),

    url(r'^submissions/discussions/top10$',
        'news_crawler.api.get_top10_discussions', name='get_top10_discussions'),

    url(r'^submissions/all/top10$',
        'news_crawler.api.get_top10_all', name='get_top10_all'),

    # url(r'^posts/(user)$', '', name=''),
    #
    # url(r'^submitters/top$', '', name=''),
    #
    # url(r'^commenters/top$', '', name=''),
    #
    # url(r'^users/most_active$', '', name=''),

]
