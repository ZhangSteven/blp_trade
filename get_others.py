# coding=utf-8
# 

from blp_trade.blp import extractOtherToXML
from blp_trade.utility import get_current_path, get_input_directory
from blp_trade.get_trade import upload
from os.path import join
from datetime import datetime
import logging
logger = logging.getLogger(__name__)



def inputFile():
	"""
	The Bloomberg XML file name
	"""
	return join(get_input_directory(), 'SENT',
				'TransToGeneva' + datetime.now().strftime('%Y%m%d') + '.xml')



def outputFile():
	"""
	The resulting XML file after trade extraction.
	"""
	return join(get_current_path(), 'uploads', 
				'BlpOthers' + datetime.now().strftime('%Y%m%d') + '.xml')




if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	outputFile = outputFile()
	extractOtherToXML(inputFile(), outputFile)
	upload(outputFile)
