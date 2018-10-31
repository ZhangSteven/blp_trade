# coding=utf-8
# 

from blp_trade.blp import extractTradesToXML
from blp_trade.utility import get_current_path, get_input_directory
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
				'TransToGeneva' + datetime.now().strftime('%Y%m%d') + '.xml')



def outputFile():
	"""
	The resulting XML file after trade extraction.
	"""
	return join(get_current_path(), 'uploads', 
				'BlpTrades' + datetime.now().strftime('%Y%m%d%H%M%S') + '.xml')



def doUpload(file):
	upload([file], getUploadConfig())



def getUploadConfig():
	"""
	Returns the upload configuration.
	"""
	config = {}
	config['winscpPath'] = r'C:\Program Files (x86)\WinSCP\WinSCP.com'
	config['timeout'] = 120
	config['scriptDir'] = r'C:\Users\steven.zhang\AppData\Local\Programs\Git\git\blp_trade\winscp_scripts'
	config['logDir'] = r'C:\Users\steven.zhang\AppData\Local\Programs\Git\git\blp_trade\winscp_logs'
	config['user'] = 'svc_sftp'
	config['password'] = 'CEcY26' 
	config['server'] = 'sftp.clamc.com.hk'
	config['targetDir'] = 'reconciliation'
	return config



if __name__ == '__main__':
	"""
	Prepare to add a command line argument, so that it does not start upload
	by default. 
	"""
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	outputFile = outputFile()
	extractTradesToXML(inputFile(), outputFile)
	doUpload(outputFile)
