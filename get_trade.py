# coding=utf-8
# 

from blp_trade.blp import extractTradesToXML
from blp_trade.utility import get_current_path, get_input_directory, getFtpConfig
from blp_trade.db import setDatabaseMode, clearTestDatabase, closeConnection
from utils.sftp import upload
from os.path import join
from datetime import datetime
import logging
logger = logging.getLogger(__name__)



def inputFile():
	"""
	The Bloomberg XML file name
	"""
	return join(get_input_directory(), 
				'TransToGeneva' + getDateString() + '.xml')



def outputFile():
	"""
	The resulting XML file after trade extraction.
	"""
	return join(get_current_path(), 'uploads', 
				'BlpTrades' + datetime.now().strftime('%Y%m%d%H%M%S') + '.xml')



def getDateString():
	"""
	return date as string in yyyymmdd format.
	"""
	return datetime.now().strftime('%Y%m%d')



def doUpload(file):
	upload([file], getFtpConfig())



if __name__ == '__main__':
	"""
	To test this module, run:

		python get_trade.py

	The above will run test files and won't do ftp upload.

	To run it in command line (test mode), do

		python get_trade.py <file>

		NOTE: no database involvement in this mode

	To run it in production mode, do

		python get_trade.py --mode production

	It will retrieve file based on today's date and do ftp upload.

	In either case, the output trade file will be stored in the 'upload'
	folder.
	"""
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('file', metavar='input file', type=str)
	parser.add_argument('--mode', nargs='?', metavar='mode', default='test')
	args = parser.parse_args()

	setDatabaseMode(args.mode)
	if args.mode == 'production':
		inputFile = inputFile()
	else:
		clearTestDatabase()	# clear test database so we can start from fresh
		inputFile = join(get_current_path(), args.file)

	try:
		outputFile = outputFile()
		extractTradesToXML(inputFile, outputFile)
		if args.mode == 'production':
			doUpload(outputFile)

	except:
		logger.exception('Error')

	finally:
		closeConnection()
	


