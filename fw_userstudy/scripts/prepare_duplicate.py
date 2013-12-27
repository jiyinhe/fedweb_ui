"""
Prepare duplicate pages
based on:
same url, same title, and same summry
"""
import db_util

db = 'fedsearch'
host = '127.0.0.1'
user = 'jhe'
pwd = 'jhe'

conn = db_util.db_connect(host, user, pwd, db)

dup_table = 'judgement_duplicate'
page_table = 'page'


def get_duplicates():
	#get all pages having same urls, titles, and summarys
	#get urls that occur more than once
	qry = 'select url, count(url), title, summary from %s group by url, title, summary'%page_table
	res = db_util.run_qry_with_results(qry, conn)			
	for r in res:
		if r[1] > 1:
			url = r[0]
			qry = 'select page_id from %s where url = "%s" order by page_id'%(page_table, url)	
			pages = db_util.run_qry_with_results(qry, conn)
			source_id = pages[0][0]
			for p in pages[1:]:
				# Fields: dup page_id, source page_id, label_type (0:automatic, 1: manual)	
				# When rerun the script, e.g., with new crawl data, update the source_id
				# if new source_id is found (Not really possible to find lower page_ids?)
				#  -- Just do this to be sure 
				qry = 'insert into %s (dup, source, label_type) values (%s, %s, 0) on duplicate key update source=%s'%(dup_table, p[0], source_id, source_id); 	
				db_util.run_qry(qry, conn)
				print p, source_id

if __name__ == '__main__':
	get_duplicates()

