"""
This script prepare the data needed in the 
experiment. We use the TREC FedWeb13 data.

Includes:
 - Topic
 - Document
 - Site
 - Run (duplicate removed)
 - Qrels
"""
import sys
import os
import db_util as db

sys.path.append(os.path.abspath('../fw_userstudy/').rsplit('/', 1)[0])
from fw_userstudy import settings


DB = settings.DATABASES['default']
user = DB['USER']
passwd = DB['PASSWORD']
database = DB['NAME']
host = DB['HOST']
conn = db.db_connect(host, user, passwd, database)




