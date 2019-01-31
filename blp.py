# coding=utf-8
# 
# Look into XML trade file generated by Bloomberg, then:
# 
# 1. Extract trades of the Quant fund.
# 2. Extract everything else (trades, trade cancellations) into a new file.
# 



import xml.etree.ElementTree as ET
from blp_trade.utility import get_current_path, get_input_directory, \
								get_portfolio_id
from blp_trade.db import lookupTrade, lookupDeletion, setDatabaseMode, \
								clearTestDatabase, saveToDB, \
								closeConnection
from os.path import join
from datetime import datetime
from functools import reduce
import logging
logger = logging.getLogger(__name__)



class KeyValueNotFound(Exception):
	pass



def extractTradesToXML(inputFile, outputFile):
	"""
	[String] input file, [String] output file => No direct output,

	Side effects:
	1. Create an output XML file with trades and deletions extracted from the 
		input XML file.

	2. Save the key values of trades or deletions into the database.

	When extractTradesToXML() is called multiple times in a day, trades in its
	output XML files won't overlap because it saves key values of trades, and
	deletions into database.	  
	"""
	logger.info('extractTradesToXML(): input {0}'.format(inputFile))
	docRoot, tradeKeys, deletionKeys = filterTrades(addRemoveHeader(fileToLines(inputFile)))

	writeXMLFile(
		ET.tostring(docRoot, encoding='utf-8', method='xml', short_empty_elements=True)
		, outputFile
	)
	saveToDB(tradeKeys, deletionKeys)



def extractOtherToXML(inputFile, outputFile):
	"""
	[String] input file, [String] output file => extract everything except 
	trades or deletions saved in database.
	"""
	logger.info('extractOtherToXML(): input {0}'.format(inputFile))
	writeXMLFile(
		ET.tostring(filterOthers(addRemoveHeader(fileToLines(inputFile)))
					, encoding='utf-8'
					, method='xml'
					, short_empty_elements=True
					)
	   , outputFile
	)



def fileToLines(file):
	"""
	[String] file => [List] lines

	read a text file and return its content as list of lines (String).
	"""
	with open(file, 'r') as f:
		return [line for line in f]



def addRemoveHeader(lines):
	"""
	[List] lines => [List] lines after taking out Geneva headers

	There are two possibilities of the XML file to process:

	1) The root elements <GenevaLoader> and <TransactionRecords> are missing,
		only child elements are there, like:

		<Sell_New>
		...
		</Sell_New>
		<Buy_New>
		...
		<Buy_New>


	2) The root elements are there, like:
	<GenevaLoader xmlns=...>
		<TransactionRecords>
			... child elements
		</TransactionRecords>
	</GenevaLoader>

	If it is case (1), then we use the <TransactionRecords> tag to wrap all the
	content; If it is case (2), then we remove <GenevaLoader> header. In either
	case, we end up with an XML document with <TransactionRecords> as the root
	element.
	"""
	if lines[0].startswith('<GenevaLoader'):
		return lines[1:len(lines)-1]
	else:
		return ['<TransactionRecords>'] + lines + ['</TransactionRecords>']



def isRightTrade(transaction):
	""" tell whether a transaction node is a trade of right portfolio """
	if isTrade(transaction) and isRightPortfolio(transaction):
		return True
	else:
		return False



def isTrade(transaction):
	""" tell whether a transaction node is a trade """
	if transaction.tag in ['Buy_New', 'Sell_New', 'SellShort_New', 'CoverShort_New']:
		return True
	else:
		return False



def isDeletion(transaction):
	""" tell whether a transaction node is a trade deletion """
	if transaction.tag in ['Buy_Delete', 'Sell_Delete', 'SellShort_Delete', 'CoverShort_Delete']:
		return True
	else:
		return False



def deletionInDB(transaction):
	"""
	[ET node] transaction => [Bool] yesno

	determine whether a trade deletion is already in DB using its key value.
	"""
	key = transaction.find('KeyValue')
	if key != None:
		return lookupDeletion(key.text)
	else:
		return False



def tradeInDB(transaction):
	"""
	[ET node] transaction => [Bool] yesno

	determine whether a trade is already in DB using its key value.
	"""
	key = transaction.find('KeyValue')
	if key != None:
		return lookupTrade(key.text)
	else:
		return False



def filterTrades(lines):
	"""
	[List] lines => A tuple consisting of the below:
		[byte string] XML content (string encoded with utf-8)
		[List] trade key values (String) of trades extracted
		[List] deleted trade key values (String) of trade deletions extracted

	The function searches for trades with the right portfolio id, as well
	as deletions of previous trades and extract those out, then create an
	XML string consisting of the above.

	The format of the input XML is as below:

	<TransactionRecords>
	... transaction records as child elements
	</TransactionRecords>

	A trade takes the following form:

	<XXX_New>
		<Portfolio>XXX</Portfolio>
		...
		<KeyValue>XXX</KeyValue>
	</XXX_New>

	Where "XXX_New" is the trade type, such as "Buy_New", "Sell_New", etc. 
	
	A trade deletion takes the following form:

	<XXX_delete>
		<KeyValue>XXXXXXX</KeyValue>
	</XXX_delete>

	Where "XXX" is the trade type, such as "Sell", "CoverShort", etc.
	"""
	def buildResult(result, transaction):
		newRoot, tradeKeys, deletionKeys = result
		if isRightTrade(transaction) and not tradeInDB(transaction):
			newRoot.append(transaction)
			tradeKeys.append(transaction.find('KeyValue').text)
		elif isDeletion(transaction) and not deletionInDB(transaction) \
			and forPreviousTrades(tradeKeys, transaction):
			newRoot.append(transaction)
			deletionKeys.append(transaction.find('KeyValue').text)

		return (newRoot, tradeKeys, deletionKeys)


	return reduce(buildResult
				  , ET.fromstringlist(lines)
				  , (ET.Element('TransactionRecords'), [], []))
# end of filterTrades()



def filterOthers(lines):
	"""
	[List] lines => [bytes] XML content (string encoded with utf-8)

	It's the opposite of filterTrades(), it filters out everything else except
	those trades or deletions already saved into the database. 
	"""
	def buildResult(newRoot, transaction):
		if isTrade(transaction) and tradeInDB(transaction):
			pass 	# no change
		elif isDeletion(transaction) and deletionInDB(transaction):
			pass 	# no change
		else:
			newRoot.append(transaction)

		return newRoot


	return reduce(buildResult
				  , ET.fromstringlist(lines)
				  , ET.Element('TransactionRecords'))



def writeXMLFile(content, filename='output.xml'):
	"""
	[bytes] (utf-8 encoded byte string )content => create a text file.

	take the content (bytes encoded as utf-8), prepand and append Geneva XML header 
	to it, then	write to a text file, return the file's full path.
	"""
	with open(filename, 'wb') as file:
		file.write(
			b'<GenevaLoader xmlns="http://www.advent.com/SchemaRevLevel758/Geneva" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.advent.com/SchemaRevLevel758/Geneva masterschema.xsd">\n' + \
			content + \
			b'\n</GenevaLoader>')



def isRightPortfolio(transaction):
	"""
	[ET node] transaction => [Bool] yesno

	the transaction looks like follows:

	<SellShort_New>
		<Portfolio>40006-C</Portfolio>
		...
	</SellShort_New>

	We need to find out whether the "Portfolio" matches what we look for.
	"""
	portfolio = transaction.find('Portfolio')
	if portfolio != None and portfolio.text.startswith(get_portfolio_id()):
		return True
	else:
		return False



def forPreviousTrades(tradeKeys, transaction):
	"""
	[List] tradeKeys, [ET node] transaction => [Bool] yesno

	the transaction looks like follows:

	<SellShort_Delete>
		<KeyValue>123235</KeyValue>
	</SellShort_Delete>

	Determine whether the transaction's keyValue is in tradeKeys or in database.
	"""
	def deletionForTrades(tradeKeys, transaction):
		keyValue = transaction.find('KeyValue')
		if keyValue != None and keyValue.text in tradeKeys:
			return True
		else:
			return False
	

	if deletionForTrades(tradeKeys, transaction) or deletionInDB(transaction):
		return True
	else:
		return False




if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('file', metavar='input file', type=str)
	args = parser.parse_args()

	#########################################################
	# IMPORTANT! 
	#
	# Set database mode to 'test' when doing command line
	#########################################################
	setDatabaseMode('test')
	clearTestDatabase()

	extractTradesToXML(args.file, 'trades_' + args.file)
	extractOtherToXML(args.file, 'others_' + args.file)
	closeConnection()