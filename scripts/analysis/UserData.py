"""
Load user data
"""
import numpy as np
import operator
import itertools
# hack to import database info form settings.py
import sys,os
sys.path.append(os.path.abspath('../../fw_userstudy/'))
sys.path.append(os.path.abspath('../../fw_userstudy/scripts/'))
from fw_userstudy import settings
import db_util as db

class UserData:
	
	def __init__(self):
		# init the DB
		database_credentials = settings.DATABASES['default']
		user = database_credentials['USER']
		passwd = database_credentials['PASSWORD']
		database = database_credentials['NAME']
		host = database_credentials['HOST']
		self.conn = db.db_connect(host, user, passwd, database)
		# set the data to empty on init
		self.data = ""

	# obtain a list with tuples of results
	def load_data(self,qry):
		self.data = db.run_qry_with_results(qry, self.conn)
		return self.data

	# convert tuples in two lists of x and y coords
	def get_x_y_data(self):
		x = [i[0] for i in self.data]
		y = [i[1] for i in self.data]
		return x,y

	# convert tuples in a array of vectors
	def get_matrix_data(self):
		d={}
		for (x,y) in self.data:
			if x in d:
				d[x].append(y)	
			else:
				d[x] = [y]
		return d.values()

if __name__ == '__main__':
	ud = UserData()
	qry = """select task_id, count(*) from fedtask_userscore as us,
auth_user as au where us.user_id=au.id group by task_id order by
count(*);"""
	data = ud.load_data(qry)
	print len(data)
	for d in data:
		print d
