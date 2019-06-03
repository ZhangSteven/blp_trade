# coding=utf-8
# 

from blp_trade.blp import extractOtherToXML
from blp_trade.utility import get_current_path, get_input_directory,\
                              getMailSender, getMailRecipients, getMailServer, \
                              getMailTimeout
from blp_trade.get_trade import doUpload, getDateString
from blp_trade.db import setDatabaseMode, clearTestDatabase, closeConnection
from utils.mail import sendMail
from os.path import join
from datetime import datetime
import logging
logger = logging.getLogger(__name__)


# To indicate whether the result is a success
SUCCESS = 1
ERROR = 0



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



def sendNotification(result, outputFile=None):
    """
    [int] result, [String] outputFile => no return value.

    The function send a notification email about the conversion result.
    """
    if result == SUCCESS:
        emailSubject = 'Bloomberg AIM trade file {0} uploaded to Geneva'.format(outputFile)
    else:
        emailSubject = 'Error occurred on flowing Bloomberg AIM trades to Geneva'


    sendMail( ''
            , emailSubject
            , getMailSender()
            , getMailRecipients()
            , getMailServer()
            , getMailTimeout())



if __name__ == '__main__':
	"""
	This program works in 3 modes:

	1. Test mode (default mode): In this case, we put the input file in local
		directory and specify the file name in command line. No upload will
		happen in this mode. The result is saved as "trade_output.xml". Use this
        mode for testing and debugging purpose.

		$ python get_others.py --file <file name>

		NOTE: Test database is used in this mode

	2. Production mode (manual): Similay to test mode, but it uses production
		database. No upload happens. Use this mode if there is something wrong
        in the auto mode.

		$ python get_others.py --mode production --file <file name>

	3. Production mode (auto): It uses production database and uploads the 
		resulting file to Geneva SFTP server. The input file comes from the
		preconfigured location and depends on the date. The output file is 
		stored in the "uploads" folder, in the form of "BlpOthers<yyyymmdd>.xml".

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
	if args.mode == 'test':
		clearTestDatabase()	# clear test database so we can start from fresh


	if args.mode == 'production' and args.file == None:	# auto mode
		inputFile = inputFile()
		outputFile = outputFile()
	else:
		inputFile = join(get_current_path(), args.file)
		outputFile = join(get_current_path(), 'trade_output.xml')


	try:
		extractOtherToXML(inputFile, outputFile)

		# Only do upload when it's in auto mode
		if args.mode == 'production' and args.file == None:
			doUpload(outputFile)
            sendNotification(SUCCESS, outputFile)

	except:
		logger.exception('Error')

        # only send notification email on error if it is in auto mode
        if args.mode == 'production' and args.file == None:
            sendNotification(ERROR)

	finally:
		closeConnection()
