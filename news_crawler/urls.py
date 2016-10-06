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

    url(r'^user/(?P<user>\w+)/posts$',
        'news_crawler.api.get_user_posts', name='get_user_posts'),

    url(r'^user/(?P<user>\w+)/posts_commented$',
        'news_crawler.api.get_user_posts_commented', name='get_user_posts_commented'),

    url(r'^user/(?P<user>\w+)/karma$',
        'news_crawler.api.get_user_karma', name='get_user_karma'),

    url(r'^statistics/submitters/top$',
        'news_crawler.api.get_top_submitters', name='get_top_submitters'),

    url(r'^statistics/commenters/top$',
        'news_crawler.api.get_top_commenters', name='get_top_commenters'),

    url(r'^statistics/most_active/top$',
        'news_crawler.api.get_top_active', name='get_top_active'),

    url(r'^statistics/most_valued/top10$',
        'news_crawler.api.get_top_valued', name='get_top_valued'),
]
