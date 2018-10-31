# coding=utf-8
# 

from blp_trade.blp import extractTradesToXML
from os.path import join
from datetime import datetime
import logging
logger = logging.getLogger(__name__)



if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)
