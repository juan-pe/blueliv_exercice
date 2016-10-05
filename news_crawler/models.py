from django.db import models
from django.utils.translation import ugettext_lazy  as _


class RedditUser(models.Model):

    name = models.CharField(
        max_length=255,
        verbose_name=_(u'Reddit user'),
        help_text=_(u'Reddit user name')
    )

    post_karma = models.IntegerField(
        verbose_name=_(u'Post karma'),
        help_text=_(u'Avarage post karma of the user'),
        null=True
    )

    comment_karma = models.IntegerField(
        verbose_name=_(u'Comment karma'),
        help_text=_(u'Avarage comment karma of the user'),
        null=True
    )

    def __str__(self):
        return self.name


class Submision(models.Model):
    submitter = models.ForeignKey(
        RedditUser,
        related_name='submissions',
        verbose_name=_(u'Reddit user'),
        help_text=_(u'Reddit user that made the submission')
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_(u'Title'),
        help_text=_(u'Title of the submision')
    )

    external_url = models.URLField(
        verbose_name=_(u'External URL'),
        help_text=_(u'External URL of the submision'),
        null=True
    )

    discusion_url = models.URLField(
        verbose_name=_(u'Discusion URL'),
        help_text=_(u'Discusion URL of the submision'),
        null=True
    )

    comments_url = models.URLField(
        verbose_name=_(u'Comments URL'),
        help_text=_(u'Comments URL of the submision'),
        null=True
    )

    submitter_url = models.URLField(
        verbose_name=_(u'Submitter URL'),
        help_text=_(u'Submiter URL of the submision'),
        null=True
    )

    punctuation = models.IntegerField(
        verbose_name=_(u'Points'),
        help_text=_(u'Points of the submision')
    )

    rank = models.IntegerField(
        verbose_name=_(u'Rank'),
        help_text=_(u'Rank of the submision')
    )

    number_of_comments = models.IntegerField(
        verbose_name=_(u'Number of comments'),
        help_text=_(u'Number of comments of the submision')
    )

    creation_date = models.DateTimeField(
        verbose_name=_(u'Creation date'),
        help_text=_(u'Creation date of the submision')
    )

    def __str__(self):
        return self.title


class Comment(models.Model):
    author = models.ForeignKey(
        RedditUser,
        related_name='comments',
        verbose_name=_(u'Reddit user'),
        help_text=_(u'Reddit user that made the comment')
    )

    submission = models.ForeignKey(
        Submision,
        related_name='comments',
        verbose_name=_(u'Submission'),
        help_text=_(u'Submission commented')
    )

    text = models.TextField(
        max_length=1024,
        verbose_name=_(u'Comment'),
        help_text=_(u'Text of the comment')
    )

    punctiation = models.IntegerField(
        verbose_name=_(u'Points'),
        help_text=_(u'Points of the comments')
    )

    creation_date = models.DateTimeField(
        verbose_name=_(u'Creation date'),
        help_text=_(u'Creation date of the comment')
    )
