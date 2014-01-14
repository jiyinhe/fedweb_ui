"""
This script removes all data from the tables
"""
import sys
import os
import db_util as db

# To import the database setting
sys.path.append(os.path.abspath('../fw_userstudy/').rsplit('/', 1)[0])
from fw_userstudy import settings
import simplejson
import xml.etree.ElementTree as et 
import re

DB = settings.DATABASES['default']
user = DB['USER']
passwd = DB['PASSWORD']
database = DB['NAME']
host = DB['HOST']
conn = db.db_connect(host, user, passwd, database)

tables = ['auth_group',
'auth_group_permissions',
'auth_permission',
'auth_user',
'auth_user_groups',
'auth_user_user_permissions',
'django_content_type',
'django_session',
'fedtask_bookmark',
'fedtask_document',
'fedtask_experiment',
'fedtask_qrels',
'fedtask_ranklist',
'fedtask_run',
'fedtask_session',
'fedtask_site',
'fedtask_task',
'fedtask_topic',
'fedtask_ui',
'fedtask_userscore',
'questionnaire_userprofile',
'registration_registrationprofile']

# Clear all tables
def clear_tables():
    for t in tables:
        print 'Clear %s table'%t
        qry = 'delete from %s'%t
        db.run_qry(qry, conn)
    # drop django_site because it wants to be special
    qry = 'drop table %s'%"django_site"
    db.run_qry(qry, conn)

clear_tables()


