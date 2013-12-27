from django.db import models
from django.contrib.auth.models import User
import operator
from whoosh.highlight import highlight, Highlighter, WholeFragmenter, HtmlFormatter
from whoosh.analysis import FancyAnalyzer
import utils
import itertools
import operator
from fw_userstudy import settings
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

class PageManager(models.Manager):
	# get the html location of the document
	def get_html_location(self, page_id):
		try:
			doc = self.get(page_id=page_id)
			html = 'pages%s'%doc.location.split('pages')[1] 
			thumb_status = Result.objects.filter(page_id=page_id)[0].thumb_status
			if thumb_status == 0:
				img = 'thumb%s'%doc.thumbnail.split('thumb')[1]
			else:
				img = None
			return html, img	
		except Page.DoesNotExist:
			return None, None	


class Page(models.Model):
    	title = models.CharField(max_length=1500, blank=True)
    	url = models.TextField(blank=True)
   	summary = models.TextField(blank=True)
    	location = models.CharField(max_length=1500, blank=True)
    	page_id = models.IntegerField(primary_key=True)
    	thumbnail = models.CharField(max_length=1500, blank=True)
    	md5 = models.CharField(max_length=96, blank=True)
	objects = PageManager()
    	class Meta:
        	db_table = u'page'

class QueryManager(models.Manager):
    	def get_query(self, qid):
        	res = self.filter(qid = qid)
    		if len(res) == 0:
			return ''
		else:
			return res[0].topicnum, res[0].text

	def get_all_queries(self):
		if settings.topics == []:
			return [(q.qid, q.topicnum, q.text) for q in self.all()]		
		else:
			qrys = [self.get(qid = q) for q in settings.topics]
			return [(q.qid, q.topicnum, q.text) for q in qrys]

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
	# Deprecated
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
			summary = page.summary
			summary = utils.clean_snippet(summary)
			#self.get_highlighted_summary(summary,query,analyzer,frag,format)
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
				'summary': summary, 
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
	def get_results_to_judge(self, qid, user_id):
		# find pages retrieved for qid
		# get results from crawls > 0 
		res = [r['page_id'] for r in Result.objects.filter(qid=qid, cid__gt=0).values('page_id').distinct()]
		# filter page_ids that didn't occur in crawl 0 
		res_c0 = [r['page_id'] for r in Result.objects.filter(qid=qid, cid=0).values('page_id').distinct()]		
		X = set(res)-set(res_c0)

		# filter page_ids that occur in the duplication table with user_id 0
		X = set([DuplicateAuto.objects.get_source_id(p) for p in X])

		pages = [Page.objects.get(page_id = p) for p in X]	

		# get actual pages, order by urls
		#pages = [Page.objects.get(page_id = page_id) for page_id in page_ids]
		pages.sort(key=(lambda x: (x.url, x.page_id)))
		#pages = Page.objects.filter(page_id__in=page_ids).order_by('url')
		# get current judgement for th page	
		#print pages
		res = [{
			'id': p.page_id,
			'title': p.title,
			'url': p.url,
			'summary': utils.clean_snippet(p.summary),
			#'location': 'pages/%s'%p.location.split('pages/')[1],
			'judge': self.get_judge(qid, user_id, p.page_id),
			'dup_source': Duplicate.objects.get_source_id(p.page_id, user_id),
			} for p in pages]
		return res
		

	def get_judge(self, qid, user_id, page_id):
		# Get judgements, if any
		jdg = Judgement.objects.filter(user_id = user_id, page = page_id, query = qid).order_by('id')

	        if len(jdg)>0:
			j = jdg[len(jdg)-1]
			if len(jdg)>1:
				jdg.delete()
			j.save()
			judge = {'relevance_snippet': j.relevance_snippet, 
				'relevance_doc': j.relevance_doc,
				}
			#if len(jdg)>1:
			#	#delete everythin except the last one
			#	for j in jdg[0:len(jdg)-1]:
			#		j.delete()	
		else:
			judge = {'relevance_snippet': 0, 'relevance_doc': 0} 	
		return judge
	
	# changed judgement table: result -> query, page	
	def save_judgement(self, user_id, qid, page_id, judge_value, judge_type, total_docs):
		print 'save_judge', qid
		# global variable
		levels = {'Nav': 6, 'Key': 5, 'HRel': 4, 'Rel': 3, 'Non': 2, 'Spam': 1};

		# Upate
		#s_count = int(progress[1])
		#p_count = int(progress[2])
		total = int(total_docs)
		# If it's already exists, update the value
		#judge = self.get(user_id = user_id, result_id = result_id)
		judges = self.filter(user_id = user_id, query = qid, page = page_id)
		if len(judges) == 1:	
			judge = judges[0]
			if judge_type == 'snippet':
				judge.relevance_snippet = levels[judge_value]
				# If document was not judged and snippet is changed to irrelvant, 
				# then also change document judge
				if levels[judge_value]<3 and judge.relevance_doc == 0:
					#print 'doc:', judge.relevance_doc, levels[judged_value]
					judge.relevance_doc = levels[judge_value]  

			elif judge_type == 'page':
				judge.relevance_doc = levels[judge_value]
			judge.save()

		# Add new judgement
		#except Judgement.DoesNotExist:
		else:
			# whether if it's empty set or larger than one entries, delete it
			# then insert new one
			if len(judges)>1:
				judges.delete()
			if judge_type == 'snippet':
				#s_count += 1
				rel_s = levels[judge_value]
				if rel_s < 3:
					rel_d = rel_s
				else:
					rel_d = 0 
			elif judge_type == 'page':
				rel_s = 0	
				rel_d = levels[judge_value]
			
			#judge = self.create(user_id=user_id, result_id=result_id, \
			#	relevance_snippet = rel_s, relevance_doc = rel_d)
			judge = self.create(user_id=user_id, query_id = qid, page_id = page_id, \
				relevance_snippet = rel_s, relevance_doc = rel_d)

			# Double check after insertion
			tmp = self.filter(user_id = user_id, query = qid, page = page_id)
			if len(tmp)>1:
				t = tmp[len(tmp)-1]
				tmp.delete()
				t.save()

		# Counts
		current_q = judge.query.qid
		#current_c = judge.result.cid

		s_count = Judgement.objects.filter(user_id = user_id, query = current_q, relevance_snippet__gt=0).count()
		p_count = Judgement.objects.filter(user_id = user_id, query = current_q, relevance_doc__gt=0).count()
		res = {
			'relevance_doc': judge.relevance_doc,
			'relevance_snippet': judge.relevance_snippet,
			's_count': s_count,
			'p_count': p_count,
			}
		print s_count, p_count, total	

		# Also if it's not in the user progress, need to create one
		try:
			UserProgress.objects.get(user_id = user_id, query_id = current_q)

		except 	UserProgress.DoesNotExist:
			p = UserProgress(user_id=user_id, query_id = qid, status=0)
			p.save()

		# update user progress
		if s_count == total and p_count == total:
			print 'query done', qid, current_q
			# finished, update the progress table
			p = UserProgress.objects.get(user_id = user_id, query_id=current_q)
			p.status = 1
			p.save()

		
		#print s_count, p_count
		return res 


class Judgement(models.Model):
	#result = models.ForeignKey(Result)
	page = models.ForeignKey(Page)
	query = models.ForeignKey(Query)
     	relevance_snippet = models.IntegerField()	
    	relevance_doc = models.IntegerField()	
    	user = models.ForeignKey(User)
	objects = JudgementManager()     

class UserProgressManager(models.Manager):
	def assign_task(self, user_id):
		# Check if there are unfinished assignment
		res = self.filter(user_id = user_id, status=0)
		if len(res)>0:
			print 'assign_task unfinished:', res[0].query.qid 
			return res[0].query.qid #res[0].crawl.cid
		else:
			# If not, find a new task, and register it
			done = self.filter(user_id=user_id, status=1)
			#done_task = [(d.query.qid, d.crawl.cid) for d in done]
			done_task = [d.query.qid for d in done]
			#done_task.sort(key=operator.itemgetter(0))
			done_task.sort()
			qid = -1
			"""
			#crawl = -1
			#all_crawls = Crawl.objects.get_crawl_ids()			
			# Check if certain crawl is not finished
			for k, g in itertools.groupby(done, lambda x: x[0]):
				done_crawls = list(g)
				remain_crawls = list(set(all_crawls)-set(done_crawls))
				if len(remain_crawls)>0:
					remain_crawls.sort()
					qid = k
					crawl = sorted(remain_crawls)[0]
			"""
			# If all crawls in these queries are done
			# find a new query
			if settings.topics == []:
				all_querys = [q.qid for q in Query.objects.all()]
			else:
				all_querys = settings.topics
			remain_queries = set(all_querys) - set(done_task)
			if len(remain_queries) > 0:
				qid = sorted(list(remain_queries))[0]
				#crawl = 1
			if not qid == -1:
				# Craete a progress profile
				#p = UserProgress(user_id=user_id, crawl_id = crawl, query_id = qid, status=0)
				p = UserProgress(user_id=user_id, query_id = qid, status=0)
				p.save()
			print 'assign_task:', qid
			return qid #crawl
	
		

class UserProgress(models.Model):
	user = models.ForeignKey(User)
	query = models.ForeignKey(Query)
	#crawl = models.ForeignKey(Crawl)
	status = models.IntegerField()
	objects = UserProgressManager()


class DuplicateManager(models.Manager):

	def register_dup(self, dup_id, source_id, user_id):
		print 'register dup'
		if dup_id == source_id:
			return [(dup_id, -1)]
		# make the smaller one as source
		dup =  max(int(dup_id), int(source_id))
		source = min(int(dup_id), int(source_id)) 		
		saved_dup = []
		try:
			# Check if the dup_id already exist, either for this user
			# or with user 0, Note: it can not exist twice among these
			d = self.get(user_id=user_id, dup = dup)
			# if exist, compare the source, always save the smallest source
			# If current source is smaller, then update everything point
			# to original source to current source
			if source < d.source:
				# create a new entry for the original source, pointing to current source 
				new_entry = Duplicate(user_id = user_id, dup = s.source, source=source)	
				new_entry.save()
				saved_dup.append((new_entry.dup, new_entry.source))
				# Find all dups of the original entry, change it to current source
				dset = self.filter(user_id = user_id, source=d.source).update(source=source)	
				saved_dup.extend([(dd.dup, dd.source) for dd in dset])
				# change the source of the original dup to current source 	
				d.source = source
				d.save()
				saved_dup.append((d.dup, d.source)) 
			# If current source is larger, pointing current source to original source
			elif source > d.source:
				new_entry = Duplicate(user_id = user_id, dup = source, source=d.source)
				new_entry.save()
				saved_dup.append((new_entry.dup, new_entry.source))
			# If it's equal, then it's a repeated submission, do nothing
		except Duplicate.DoesNotExist:
			# If the dup does not exist yet
			# find if the source is a dup in the db
			d = self.filter(user_id=user_id, dup=source)	
			if len(d)>1:
				print 'Error: multilpe entries with the same dup id'	
			elif len(d) == 1:
				# if source is dup in the db, add the new entry for the original source
				new_entry = Duplicate(user_id=user_id, dup=dup, source=d[0].source)		
				new_entry.save()
				saved_dup.append((new_entry.dup, new_entry.source))
			else:
				# if source is not a dup, then either it's an original source
				# or neither a dup nor a source, then add this entry
				new_entry = Duplicate(user_id=user_id, dup=dup, source=source)
				new_entry.save()
				saved_dup.append((new_entry.dup, new_entry.source))	

		return saved_dup

	def delete_dup(self, dup_id, source_id, user_id):
		# Check if dup already exist
		# print "empty source"
		dup_id = int(dup_id)
		source_id = int(source_id)
		dup = max(dup_id, source_id)
		source = min(dup_id, source_id)
		saved_dup = [] 	
		try:	
			# If exists, remove that item
			d = self.get(user_id=user_id, dup=dup, source=source)
			d.delete()
			# check if source is still source
			s = self.filter(user_id=user_id, source=source)
			if len(s)>0:
				saved_dup = [(dup, '')]
			else:
				saved_dup = [(dup, ''), (source, '')]
			return saved_dup

		except Duplicate.DoesNotExist:
			return saved_dup
 
	def get_source_id(self, dup_id, user_id):
		try:
			source_id = self.get(dup=dup_id, user_id=user_id).source
			return source_id
		except Duplicate.DoesNotExist:
			source_id = self.filter(user_id=user_id, source=dup_id)
			if len(source_id)>0:
				return 'Source'
			else:
				return '' 

# automatically detected and manually detected duplicate pages
class Duplicate(models.Model):
	dup = models.IntegerField()
	source = models.IntegerField()
	# 0: automatically detected, Others are associated other user_ids 
	user_id = models.IntegerField()
	#url = models.TextField() 
	#source_url = models.TextField()
	objects = DuplicateManager()


class DuplicateAutoManager(models.Manager):
	def get_source_id(self, page_id):
		try:
			return self.get(dup = page_id).source
		except DuplicateAuto.DoesNotExist:
			return page_id

class DuplicateAuto(models.Model):
	dup = models.IntegerField(primary_key=True)
	source = models.IntegerField()
	objects = DuplicateAutoManager()

	
	
	

