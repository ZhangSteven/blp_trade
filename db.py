# coding=utf-8
# 
# Store some records in MySQL database
#

import pymysql
from blp_trade.utility import getDbName, getDbHost, getDbUser, getDbPassword
import logging
logger = logging.getLogger(__name__)



class InvalidDBOperation(Exception):
	pass



def tradeInDB(keyValue):
	"""
	Use the trade key value to determine whether it is in database.
	"""
	with getConnection().cursor() as cursor:
		try:
			sql = "SELECT key_value FROM trade WHERE key_value='{0}'".format(keyValue)
			cursor.execute(sql)
			row = cursor.fetchone()
			if row != None:	# found
				return True
			else:
				return False

		except:
			logger.exception('tradeInDB(): ')



def deletionInDB(keyValue):
	"""
	Use the deletion key value to determine whether it is in database.
	"""
	with getConnection().cursor() as cursor:
		try:
			sql = "SELECT deleted FROM trade WHERE key_value='{0}'".format(keyValue)
			cursor.execute(sql)
			row = cursor.fetchone()
			if row != None and row['deleted'] == '1':
				return True
			else:
				return False

		except:
			logger.exception('deletionInDB(): ')



def saveToDB(tradeKeys, deletionKeys):
	saveTrades(tradeKeys)
	saveDeletions(deletionKeys)



def saveTrades(tradeKeys):
	"""
	[List] tradeKeys

	save the list of keys of new trades into the database
	"""
	with getConnection().cursor() as cursor:
		try:
			sql = "INSERT INTO trade (key_value, deleted) VALUES (%s, '0')"
			cursor.executemany(sql, tradeKeys)
			connection.commit()

		except:
			logger.exception('saveTrades(): ')



def saveDeletions(deletionKeys):
	"""
	[List] deletionKeys

	save the list of keys of deletions into the database. Because a deletion is
	only valid if that trade key value is already in the database, therefore
	we use UPDATE here.
	"""
	with getConnection().cursor() as cursor:
		try:
			sql = "UPDATE trade SET deleted = '1' WHERE key_value = (%s)"
			cursor.executemany(sql, deletionKeys)
			connection.commit()

		except:
			logger.exception('saveDeletions(): ')


# def saveResultsToDB(directory, resultList):
# 	"""
# 	input: [String] directory, [Iterable] resultList
# 	output: save the results into database

# 	where directory is the directory containing the files, and resultList
# 	is a list of tuple (file, status), status is either 0 or 1.
# 	"""
# 	def toDBRecord(result):
# 		"""
# 		([String] file, [Int] status) => 
# 			([String] file, [String] datetime, [String] status)
# 		"""
# 		file, status, _, _ = result
# 		return (file
# 				, strftime('%Y-%m-%d %H:%M:%S', localtime(getmtime(join(directory, file))))
# 				, str(status))

# 	# we need to convert to list first and tell whether it's empty because
# 	# emtpy list will cause cursor.executemany() to fail
# 	records = list(map(toDBRecord, resultList))
# 	if records == []:
# 		logger.debug('saveResultsToDB(): no records to save')
# 		return


# 	try:
# 		with connection.cursor() as cursor:
# 			sql = "REPLACE INTO file (file_name, last_modified, status) \
# 					VALUES (%s, %s, %s)"
# 			cursor.executemany(sql, records)

# 			# save changes
# 			connection.commit()

# 	except:
# 		logger.exception('saveResultsToDB(): ')

mode = 'test'	# default is test mode
def setDatabaseMode(m):
	"""
	Different mode determines which data base to connect (test or production)
	"""
	global mode
	mode = m



connection = None
def getConnection():
	global connection
	if connection == None:
		global mode
		connection = initializeConnection(mode)
		
	return connection



def initializeConnection(mode):
	if mode == 'production':
		logger.info('getConnection(): establish DB connection, production mode')
		return pymysql.connect(host=getDbHost('production'),
									user=getDbUser('production'),
									password=getDbPassword('production'),
									db=getDbName('production'),
									cursorclass=pymysql.cursors.DictCursor)

	else:
		logger.info('getConnection(): establish DB connection, test mode')
		return pymysql.connect(host=getDbHost('test'),
									user=getDbUser('test'),
									password=getDbPassword('test'),
									db=getDbName('test'),
									cursorclass=pymysql.cursors.DictCursor)



def clearTestDatabase():
	"""
	Delete all contents in test database.

	This function is for unit test purpose only, it should NEVER be called in
	production mode.
	"""
	global mode
	if mode == 'production':
		raise InvalidDBOperation()


	try:
		with getConnection().cursor() as cursor:
			sql = "DELETE FROM trade"
			cursor.execute(sql)

			# save changes
			getConnection().commit()

	except:
		logger.exception('clearTestDatabase(): ')



def closeConnection():
	global connection
	if connection != None:
		logger.info('DB connection closed')
		connection.close()



if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)
	
	setDatabaseMode('test')
	clearTestDatabase();
	closeConnection()

# 	# Works
# 	# try:
# 	# 	with connection.cursor() as cursor:
# 	# 		# create a new record
# 	# 		sql = "INSERT INTO `trade_file` (`file_name`, `last_modified`, `status`) \
# 	# 				VALUES (%s, %s, %s)"
# 	# 		cursor.execute(sql, ('Trade File 20190117.xlsx'
# 	# 							, '2019-01-20 10:05:22'
# 	# 							, '0')
# 	# 						)

# 	# 		# save changes
# 	# 		connection.commit()

# 	# finally:
# 	# 	connection.close()

# 	print(lookupLastModifiedTime('Trade File 20190116.xlsx'))
# 	closeConnection()