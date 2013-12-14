from django.db import models
from django.contrib.auth.models import User


# Create your models here.
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class Crawl(models.Model):
    status = models.IntegerField(null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    cid = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'crawl'


class Page(models.Model):
    title = models.CharField(max_length=1500, blank=True)
    url = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    location = models.CharField(max_length=1500, blank=True)
    page_id = models.IntegerField(primary_key=True)
    thumbnail = models.CharField(max_length=1500, blank=True)
    md5 = models.CharField(max_length=96, blank=True)
    class Meta:
        db_table = u'page'

class Query(models.Model):
    qid = models.IntegerField(primary_key=True)
    topicnum = models.CharField(max_length=765, blank=True)
    text = models.CharField(max_length=1500, blank=True)
    class Meta:
        db_table = u'query'


class Site(models.Model):
    description = models.CharField(max_length=1500, blank=True)
    desc_url = models.CharField(max_length=765, blank=True)
    template = models.TextField(blank=True)
    sid = models.IntegerField(primary_key=True)
    open_search = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=765, blank=True)
    class Meta:
        db_table = u'site'


class Result(models.Model):
    #qid = models.IntegerField(null=True, blank=True)
    query = models.ForeignKey(Query)	
    rank = models.IntegerField(null=True, blank=True)
    thumb_status = models.CharField(max_length=765, blank=True)
    crawl_time = models.DateTimeField()
    thumb_time = models.DateTimeField()
    #cid = models.IntegerField(null=True, blank=True)
    crawl = models.ForeignKey(Crawl)	
    #sid = models.IntegerField(null=True, blank=True)
    site = models.ForeignKey(Site)
    #page_id = models.BigIntegerField(null=True, blank=True)
    page = models.ForeignKey(Page)
    crawl_status = models.CharField(max_length=765, blank=True)
    class Meta:
        db_table = u'result'

class Judgement(models.Model):
    result = models.ForeignKey(Result)
    relevance = models.IntegerField()	
    user = models.ForeignKey(User)
     
