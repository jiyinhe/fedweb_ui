import db_util as db
import os
import sys
# to import the database setting
sys.path.append(os.path.abspath('../fw_userstudy/').rsplit('/', 1)[0])
from fw_userstudy import settings

DB = settings.DATABASES['default']
user = DB['USER']
passwd = DB['PASSWORD']
database = DB['NAME']
host = DB['HOST']
conn = db.db_connect(host, user, passwd, database)


def fix_table_results():
	qry = 'alter table Result add column `id` int(10) unsigned primary KEY AUTO_INCREMENT;'
	db.run_qry(qry, conn)

if __name__ == '__main__':
	fix_table_results()

