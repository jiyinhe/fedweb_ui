from django.db import models
from django.contrib.auth.models import User
import operator
from whoosh.highlight import highlight, Highlighter, WholeFragmenter, HtmlFormatter
from whoosh.analysis import FancyAnalyzer

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

class CrawlManager(models.Manager):
	def get_crawl_ids(self):
		return [r.cid for r in self.all()]


class Crawl(models.Model):
	status = models.IntegerField(null=True, blank=True)
    	start_date = models.DateTimeField()
    	end_date = models.DateTimeField()
    	cid = models.IntegerField(primary_key=True)
	objects = CrawlManager()
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

class QueryManager(models.Manager):
    	def get_query(self, qid):
        	res = self.filter(qid = qid)
    		if len(res) == 0:
			return ''
		else:
			return res[0].topicnum, res[0].text

class Query(models.Model):
    	qid = models.IntegerField(primary_key=True)
    	topicnum = models.CharField(max_length=765, blank=True)
    	text = models.CharField(max_length=1500, blank=True)
    	objects = QueryManager()
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

class ResultManager(models.Manager):
	def get_results(self, crawl_id, qid, user_id):
		crawl_id = int(crawl_id)
		qid = int(qid)

		frag = WholeFragmenter()
		analyzer = FancyAnalyzer()
		format = HtmlFormatter(tagname="b")
		# get the query for highlighting
		query = [q.text for q in analyzer(Query.objects.get(qid=qid).text)]

		res = self.filter(qid = qid, cid = crawl_id)
		page_res = dict([(r.page_id, r) for r in res])
		page_ids = page_res.keys()

		# Get urls of pages
		pages = Page.objects.filter(page_id__in = page_ids)
		page_url = dict([(p.url, p) for p in pages])
		urls = set([p.url for p in pages])

		# Get urls of previous crawl
		res2 = self.filter(qid = qid, cid = (crawl_id-1))		
		page_ids2 = [r.page_id for r in res2]
		pages2 = Page.objects.filter(page_id__in = page_ids2)
		urls2 = set([p.url for p in pages2])
	
		# Get the new pages
		new_urls = urls.difference(urls2)
		new_res = []	
		for u in new_urls:
			page = page_url[u]			
			r = page_res[page.page_id]
			site = Site.objects.get(sid = r.sid) 
			# Get judgements, if any
			try:
				j = Judgement.objects.get(user_id = user_id, result_id = r.id)		
				judge = {'relevance_snippet': j.relevance_snippet, 
					'relevance_doc': j.relevance_doc,
					}
			except Judgement.DoesNotExist:
				judge = {'relevance_snippet': 0, 'relevance_doc': 0} 	

			item = {
				'site_id':r.sid, 
				'site_name': site.name,
				'title': page.title, 
				'url': page.url,
				'summary': self.get_highlighted_summary(page.summary,query,analyzer,frag,format),
				'location': page.location.split('fedsearch_crawl/')[1],
				'rank': r.rank,
				'id': r.id,
				'judge': judge,
				} 
			new_res.append((item, r.sid, r.rank))
		return sorted(new_res, key=operator.itemgetter(1, 2))


	def get_highlighted_summary(self,summary,query, analyzer,frag,format):
		#summary = unicode(summary.replace('\n', ' '))
		#if len(summary) > 350:
		#	summary = unicode(summary.replace('\n', ' '))[0:350]+'...'
		hl = highlight(summary,query,analyzer,frag,format)
		if hl:
			return hl
		else:
			return summary


class Result(models.Model):
	id = models.IntegerField(primary_key = True)
    	qid = models.IntegerField(null=True, blank=True)
    	#query = models.OneToOneField(Query)	
    	rank = models.IntegerField(null=True, blank=True)
    	thumb_status = models.CharField(max_length=765, blank=True)
    	crawl_time = models.DateTimeField()
    	thumb_time = models.DateTimeField()
    	cid = models.IntegerField(null=True, blank=True)
    	#cid = models.ForeignKey(Crawl)	
    	sid = models.IntegerField(null=True, blank=True)
    	#sid = models.ForeignKey(Site)
    	page_id = models.BigIntegerField(null=True, blank=True)
    	#page = models.ForeignKey(Page)
    	crawl_status = models.CharField(max_length=765, blank=True)
	objects = ResultManager()

    	class Meta:
        	db_table = u'result'

class JudgementManager(models.Manager):
	def save_judgement(self, user_id, result_id, judge_value, judge_type):
		# global variable
		levels = {'Nav': 6, 'Key': 5, 'HRel': 4, 'Rel': 3, 'Non': 2, 'Spam': 1};

		#print updated_values
		try:
			judge = self.get(user_id = user_id, result_id = result_id)
			if judge_type == 'snippet':
				judge.relevance_snippet = levels[judge_value]
			elif judge_type == 'page':
				judge.relevance_doc = levels[judge_value]
			judge.save()

		except Judgement.DoesNotExist:
			if judge_type == 'snippet':
				rel_s = levels[judge_value]
				if rel_s < 3:
					rel_d = rel_s
				else:
					rel_d = 0 
			elif judge_type == 'page':
				rel_s = 0	
				rel_d = levels[judge_value]

			judge = self.create(user_id=user_id, result_id=result_id, \
				relevance_snippet = rel_s, relevance_doc = rel_d)
		res = {
			'relevance_doc': judge.relevance_doc,
			'relevance_snippet': judge.relevance_snippet,
			}	

		return res 

class Judgement(models.Model):
	result = models.ForeignKey(Result)
     	relevance_snippet = models.IntegerField()	
    	relevance_doc = models.IntegerField()	
    	user = models.ForeignKey(User)
	objects = JudgementManager()     
