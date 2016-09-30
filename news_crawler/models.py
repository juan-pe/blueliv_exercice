from django.db import models


class Submision(models.Model):
    pass


class User(models.Model):

    name = models.CharField(
        max_lenght=255
    )
    pass


class Comments(models.Model):
    pass
