from django.db import models
from django.utils.translation import ugettext_lazy  as _


class RedditUser(models.Model):

    name = models.CharField(
        max_length=255,
        verbose_name=_(u'Reddit user'),
        help_text=_(u'Reddit user name')
    )

    def __str__(self):
        return self.name


class Submision(models.Model):
    submision_title = models.CharField(
        max_length=255,
        verbose_name=_(u'Title'),
        help_text=_(u'Title of the submision')
    )

    external_url = models.URLField(
        verbose_name=_(u'External URL'),
        help_text=_(u'External URL of the submision')
    )

    discusion_url = models.URLField(
        verbose_name=_(u'Discusion URL'),
        help_text=_(u'Discusion URL of the submision')
    )

    submitter = models.ForeignKey(
        RedditUser,
        verbose_name=_(u'Reddit user'),
        help_text=_(u'Reddit user that made the submission')
    )

    punctiation = models.IntegerField(
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


# class Comments(models.Model):
#     pass
