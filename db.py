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
	return False



def deletionInDB(keyValue):
	"""
	Use the deletion key value to determine whether it is in database.
	"""
	return False	





# def lookupLastModifiedTime(file):
# 	"""
# 	[String] file => [Datetime] last modified time of file in DB.

# 	if lookup does not find any record in database, return None
# 	"""
# 	try:
# 		with getConnection().cursor() as cursor:
# 			sql = "SELECT last_modified FROM file WHERE file_name='{0}'".format(file)
# 			cursor.execute(sql)
# 			row = cursor.fetchone()
# 			if row == None:
# 				logger.debug('lookupLastModifiedTime(): {0} not found'.format(file))
# 				return None
# 			else:
# 				return row['last_modified']

# 	except:
# 		logger.exception('lookupLastModifiedTime(): ')



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