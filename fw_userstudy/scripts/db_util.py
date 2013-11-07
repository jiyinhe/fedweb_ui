import MySQLdb


def db_connect(host, user, pwd, db):
        try:
                db = MySQLdb.connect(host, user, pwd, db)
        except Exception:
                print "not conneted"
        return db

def run_qry(qry, conn):
        try:
               conn.query(qry)
        except Exception, e:
               conn.ping(True)
               print qry
               print e

def run_qry_with_results(qry, conn):
        try:
                conn.query(qry)
        except Exception, e:
                conn.ping(True)
                print qry
                print e
        r = conn.store_result()
        res = r.fetch_row(0)
        return res

