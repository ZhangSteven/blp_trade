# coding=utf-8
# 

from blp_trade.blp import extractOtherToXML
from blp_trade.utility import get_current_path, get_input_directory
from blp_trade.get_trade import doUpload, getDateString
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
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('--mode', nargs='?', metavar='mode', default='test')
	args = parser.parse_args()

	if args.mode == 'production':
		inputFile = inputFile()
	else:
		inputFile = join(get_current_path(), 'samples', 'TransToGeneva20181031_full.xml')

	try:
		outputFile = outputFile()
		extractOtherToXML(inputFile, outputFile)
		if args.mode == 'production':
			doUpload(outputFile)
	
	except:
		logger.exception('Error')