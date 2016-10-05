import logging
from datetime import datetime
from dateutil import parser

from django.db.models import Q

from news_crawler.models import RedditUser, Submision, Comment

logger = logging.getLogger(__name__)

__all__ = ['process_submission', 'get_submision_title', 'get_submision_submitter',
           'get_submision_url', 'get_submision_creation_date', 'get_submision_creation_date',
           'get_submision_punctuation', 'get_submision_punctuation', 'get_submision_rank',
           'get_submisions_comments', 'get_comments_url', 'get_submitter_url',
           'get_user_comment_karma', 'get_user_karma', 'process_comment',
           'get_comment_author', 'get_comment_text', 'get_comment_punctuation',
           'get_comment_creation_date']

def process_submission(submision):
    '''
    Function that from a python subreddit submision extract:
        - submisions title
        - externals url
        - discusion url
        - submitter
        - punctuation
        - creation_date
        - number_of_comments
        - comments
        - users
    and save them into db
    '''
    sub = {}
    submission = None
    sub['title'] = get_submision_title(submision)

    if 'self' not in submision.get('class'):
        sub['external_url'] = get_submision_url(submision)
    else:
        sub['discusion_url'] = get_submision_url(submision)

    sub['submitter'] = get_submision_submitter(submision)
    sub['punctuation'] = get_submision_punctuation(submision)
    sub['rank'] = get_submision_rank(submision)
    sub['creation_date'] = get_submision_creation_date(submision)
    sub['number_of_comments'] = get_submisions_comments(submision)
    sub['comments_url'] = get_comments_url(submision)
    sub['submitter_url'] = get_submitter_url(submision)

    qsub = Q(submitter=sub['submitter'], title=sub['title'])
    try:
        submisions = Submision.objects.filter(qsub)
        if submisions.exists():
            submisions.update(**sub)
            submission = submisions.first()
        else:
            submission = Submision.objects.create(**sub)
    except Exception as e:
        logger.exception(e)

    return submission


def get_submision_title(submision):
    title_fields = submision.cssselect('a[class^="title"]')
    return title_fields[0].text if title_fields else ''


def get_submision_url(submision):
    return submision.get('data-url')


def get_submision_submitter(submision):
    author = submision.get('data-author')
    return RedditUser.objects.get_or_create(name=author)[0]


def get_submision_creation_date(submision):
    time_stamp = submision.get('data-timestamp')
    return datetime.utcfromtimestamp(int(time_stamp)/1000)


def get_submision_punctuation(submision):
    punctuation_elem = submision.cssselect('[class="score unvoted"]')
    if punctuation_elem and punctuation_elem[0].text != u'•':
        return int(punctuation_elem[0].text)

    return 0


def get_submision_rank(submision):
    rank = submision.get('data-rank')
    return int(rank) if rank else 0


def get_submisions_comments(submision):
    comments = submision.cssselect('li > a[class~="comments"]')
    if comments:
        if len(comments[0].text.split(' ')) == 2:
            return int(comments[0].text.split(' ')[0])
    return 0


def get_comments_url(submision):
    comments_elem = submision.cssselect('li > a[class~="comments"]')
    return comments_elem[0].get('href') if comments_elem  else ''


def get_submitter_url(submison):
    submitter_url_elem = submison.cssselect('p > a[class~="author"]')
    return submitter_url_elem[0].get('href') if submitter_url_elem else ''


def get_user_comment_karma(dom):
    user_commment_karma_elem = dom.cssselect('div > span[class="karma comment-karma"]')
    if user_commment_karma_elem:
        karma = user_commment_karma_elem[0].text.replace(',', '')
        return int(karma)
    return 0


def get_user_karma(dom):
    user_karma_elem = dom.cssselect('div > span[class="karma"]')
    if user_karma_elem:
        karma = user_karma_elem[0].text.replace(',', '')
        return int(karma)
    return 0


def process_comment(comment, submission):
    from news_crawler.tasks import get_and_process_user_page
    '''
    Function that from a python subreddit comment extract:
        - author
        - text
        - punctiation
        - creation_date
    and save them into db
    '''
    com = {
        'submission': submission
    }
    com['author'] = get_comment_author(comment)
    com['text'] = get_comment_text(comment)
    com['punctiation'] = get_comment_punctuation(comment)
    com['creation_date'] = get_comment_creation_date(comment)
    try:
        com_object = Comment.objects.create(**com)
    except Exception as e:
        com_object = None
        logger.exception(e)

    if com['author'] and (not com['author'].post_karma or not com['author'].comment_karma):
        url = get_submitter_url(comment)
        get_and_process_user_page(url, com['author'])

    return com_object


def get_comment_author(comment):
    author_elem = comment.cssselect('p > a[class~="author"]')
    author = author_elem[0].text if author_elem else ''

    return RedditUser.objects.get_or_create(name=author)[0] \
           if author else None


def get_comment_text(comment):
    comment_text_elem = comment.cssselect(
        'div[class~="usertext-body"] > div[class="md"]')

    return comment_text_elem[0].text_content().strip() \
           if comment_text_elem else ''


def get_comment_punctuation(comment):
    comment_punctuation_elem = comment.cssselect(
        'p > span[class="score unvoted"]')
    return int(comment_punctuation_elem[0].text.split(' ')[0]) \
           if comment_punctuation_elem else 0


def get_comment_creation_date(comment):
    comment_creation_date_elem = comment.cssselect(
        'p > time[class="live-timestamp"]')
    return parser.parse(comment_creation_date_elem[0].get('datetime'), ignoretz=True) \
           if comment_creation_date_elem else None
