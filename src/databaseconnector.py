import sqlite3 as sql
from playhouse.sqlcipher_ext import *

db_ref = SqlCipherDatabase(None)

class DatabaseConnector:

    DBPREFIX = 'btf_'

    DBConnector = None

    def __init__(self, password):
        print('...initializing database')
        outer_ref = self

        try:
            db_ref.init('bitifier.enc', passphrase=password)
            self.DBConnector = db_ref

            #http://charlesleifer.com/blog/encrypted-sqlite-databases-with-python-and-sqlcipher/
            #http://docs.peewee-orm.com/en/latest/peewee/models.html

            '''DBConnector = sql.connect('bitifier.db')

            cursor = DBConnector.cursor()
            cursor.execute('CREATE TABLE ' + self.DBPREFIX + 'tracking ('
                                                              'id INTEGER PRIMARY KEY,'
                                                             'user_id INTEGER,'
                                                             'trans_id INTEGER,'
                                                             'date INTEGER,'
                                                             'dep_balance REAL,'
                                                             'swap_payment REAL,'
                                                             'average_return REAL,'
                                                             'UNIQUE(user_id, trans_id)'
                                                             ');')

            cursor.execute('CREATE TABLE ' + self.DBPREFIX + 'users ('
                                                             'id INTEGER PRIMARY KEY,'
                                                             'name TEXT,'
                                                             'email TEXT,'
                                                             'password TEXT,'
                                                             'bfxapikey TEXT,'
                                                             'bfxapisec TEXT,'
                                                             'status INTEGER'
                                                             ');')
            cursor.execute('CREATE TABLE ' + self.DBPREFIX + 'vars ('
                                                             'id INTEGER PRIMARY KEY,'
                                                             'minlendrate TEXT,'
                                                             'spreadlend TEXT,'
                                                             'USDgapbottom TEXT,'
                                                             'USDgaptop TEXT,'
                                                             'thirtydaymin TEXT,'
                                                             'highholdlimit TEXT,'
                                                             ');')

            cursor.execute('CREATE TABLE ' + self.DBPREFIX + 'cronruns ('
                                                             'id INTEGER PRIMARY KEY,'
                                                             'cron_id INTEGER,'
                                                             'lastrun INTEGER,'
                                                             'details TEXT'
                                                             ');')

            '''

        except sql.DatabaseError:
            print('Database error - could not open database or create tables')

        except sql.Error:
            print('Database error - unknown database error occurred.')

        finally:
            if self.DBConnector:
                self.DBConnector.close()

    class BtfModel(Model):
        class Meta:
            database = db_ref

    class Statistics(BtfModel):
        id = PrimaryKeyField()
        user_id = IntegerField(unique=True)
        trans_id = IntegerField(unique=True)
        date = DateField()
        depbalance = DecimalField(max_digits=14, decimal_places=2)
        swappayment = DecimalField(max_digits=14, decimal_places=2)
        averagereturn = DecimalField(max_digits=14, decimal_places=6)


    class User(BtfModel):
        id = PrimaryKeyField()
        name = CharField()
        email = CharField()
        password = CharField()
        bfxapikey = CharField(max_length=64)
        bfxapisec = CharField(max_length=64)
        status = BooleanField()

    class Variables(BtfModel):
        id = PrimaryKeyField()
        minlendrate = CharField(max_length=12)
        spreadlend = CharField(max_length=12)
        USDgapbottom = CharField(max_length=12)
        USDgaptop = CharField(max_length=12)
        thirtydaymin = CharField(max_length=12)
        highholdlimit = CharField(max_length=12)
        highholdamt = CharField(max_length=12)

    class CronRuns(BtfModel):
        id = PrimaryKeyField()
        cronid = IntegerField(null=False)
        lastrum = DateField(null=False)
        details = TextField(null=False)


'''$trackingSQL = 'CREATE TABLE `'.$tablePre.'Tracking` (
			  `id` int(12) NOT NULL AUTO_INCREMENT,
			  `user_id` smallint(4) DEFAULT NULL,
			  `trans_id` int(12) DEFAULT NULL,
			  `date` date DEFAULT NULL,
			  `dep_balance` decimal(12,2) DEFAULT NULL,
			  `swap_payment` decimal(12,2) DEFAULT NULL,
			  `average_return` decimal(8,6) DEFAULT NULL,
			  PRIMARY KEY (`id`),
			  UNIQUE KEY `uniquieKeys` (`user_id`,`trans_id`)
			) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=latin1';
			'''


'''import sqlite3 as lite
import sys

con = None

try:
    con = lite.connect('test.db')

    cur = con.cursor()
    cur.execute('SELECT SQLITE_VERSION()')

    data = cur.fetchone()

    print "SQLite version: %s" % data

except lite.Error, e:

    print "Error %s:" % e.args[0]
    sys.exit(1)

finally:

    if con:
        con.close()
'''