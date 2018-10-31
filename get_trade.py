# coding=utf-8
# 

from blp_trade.blp import extractTradesToXML
from blp_trade.utility import get_current_path, get_input_directory
from os.path import join
from datetime import datetime
import logging
logger = logging.getLogger(__name__)



def inputFile():
	"""
	The Bloomberg XML file name
	"""
	return join(get_input_directory(), 
				'TransToGeneva' + datetime.now().strftime('%Y%m%d') + '.xml')



def outputFile():
	"""
	The resulting XML file after trade extraction.
	"""
	return join(get_current_path(), 'uploads', 
				'BlpTrades' + datetime.now().strftime('%Y%m%d%H%M%S') + '.xml')



def upload(files):
	pass



if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	outputFile = outputFile()
	extractTradesToXML(inputFile(), outputFile)
	upload([outputFile])
