# coding=utf-8
# 

from blp_trade.blp import extractOtherToXML
from blp_trade.utility import get_current_path, get_input_directory
from blp_trade.get_trade import doUpload, getDateString
from blp_trade.db import setDatabaseMode, clearTestDatabase, closeConnection
from os.path import join
from datetime import datetime
import logging
logger = logging.getLogger(__name__)



def inputFile():
	"""
	The Bloomberg XML file name
	"""
	return join(get_input_directory(), 'SENT',
				'TransToGeneva' + getDateString() + '.xml')



def outputFile():
	"""
	The resulting XML file after trade extraction.
	"""
	return join(get_current_path(), 'uploads', 
				'BlpOthers' + getDateString() + '.xml')




if __name__ == '__main__':
	"""
	This program works in two modes:

	1. Test mode: the default mode. In this case, it reads an XML file in local
		directory, run as below:

		$ python get_others.py --file <file name>

		NOTE: no database involvement in this mode

	2. Production mode: It reads an XML from a preconfigured directory and the
		file name is based on the date. The output file will be uploaded to
		Geneva SFTP server. Run as below:

		$ python get_others.py --mode production
	"""
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('--file', nargs='?', metavar='input file', type=str)
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
		extractOtherToXML(inputFile, outputFile)
		if args.mode == 'production':
			doUpload(outputFile)
	
	except:
		logger.exception('Error')

	finally:
		closeConnection()