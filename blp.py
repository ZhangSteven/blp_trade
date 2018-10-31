# coding=utf-8
# 
# Look into XML trade file generated by Bloomberg, then:
# 
# 1. Extract trades of the Quant fund.
# 2. Extract everything else (trades, trade cancellations) into a new file.
# 
# What to do next:
# 
# 1. What do other actions look like: cancel or correct tickets?
# 2. What if we add or changed trades after the trade upload at 12:00pm, say
# 		3pm? In the current logic, those added trades after 12:00pm will also
# 		be filter out at 10:00pm upload. So is there a way to upload the
# 		incremental part? Maybe we can use the ticket number to handle:
# 		uploaded trades' have their ticket numbers stored somewhere, then when
# 		we do another extract and upload process, it will only extract those
# 		not uploaded trades.



import xml.etree.ElementTree as ET
from os.path import join
from datetime import datetime
import logging
logger = logging.getLogger(__name__)



class KeyValueNotFound(Exception):
	pass



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



def filterTrades(lines, skipKeys):
	"""
	[List] lines, [List] skipKeys => [bytes] XML content (string encoded with 
															utf-8)

	The function searches for trades with the right portfolio id and
	extract those trades out, the result is returned as an XML string. 
	As a side effect, it saves the list of key values of those trades.

	During the search, if the key value of a trade found is in the list
	of skipKeys, then the trade won't be extracted.

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
	
	Note that trade cancellations won't be captured, because cancellation
	takes the below form:

	<XXX_delete>
		<KeyValue>XXXXXXX</KeyValue>
	</XXX_delete>

	Where "XXX" is the trade type, such as "Sell", "CoverShort", etc.

	For trade corrections, since a correction is just cancellation + new
	trade, only the new trade part will be captured.
	"""
	root = ET.fromstringlist(lines)
	newRoot = ET.Element('TransactionRecords')
	keyList = []
	for transaction in root:
		portfolio = transaction.find('Portfolio')
		if portfolio != None and isRightPortfolio(portfolio.text):
			try:
				keyValue = transaction.find('KeyValue').text
				if not keyValue in skipKeys:
					keyList.append(keyValue)
					newRoot.append(transaction)
			except:
				raise KeyValueNotFound()

	# save the transaction keys to somewhere (text file)
	saveKeys(keyList)

	# generate XML as an utf-8 encoded byte string
	return ET.tostring(newRoot, encoding='utf-8', method='xml', short_empty_elements=True)



def inverseFilterTrades(lines):
	"""
	[List] lines => [bytes] XML content (string encoded with utf-8)

	It's the opposite of filterTrades(), it keeps out those trades with the
	right portfolio id, the rest will be 
	"""
	root = ET.fromstringlist(lines)
	newRoot = ET.Element('TransactionRecords')
	for transaction in root:
		portfolio = transaction.find('Portfolio')
		if portfolio == None or not isRightPortfolio(portfolio.text):
			newRoot.append(transaction)

	return ET.tostring(newRoot, encoding='utf-8', method='xml', short_empty_elements=True)



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
			b'</GenevaLoader>')




def isRightPortfolio(portId):
	"""
	[String] portId => [Bool] yesno

	Determine whether the portfolio id is of interest.
	"""
	if portId.startswith('40006'):
		return True
	else:
		return False



def saveKeys(keyList):
	"""
	[List] key list => write the list of keys (string) to a text file.
	"""
	if keyList == []:
		return

	with open(getFilename(), 'a') as textFile:
		for key in keyList:
			print(f'{key}', file=textFile)



def loadKeys():
	"""
	Read a text file => [List] keys
	"""
	try:
		textFile = open(getFilename(), 'r')
		return [line.strip() for line in textFile]
	except FileNotFoundError:
		return []



def getFilename():
	"""
	return the text file name for today.

	Text files storing keys are stored and named as:

	keyFiles/keys_yyyymmdd.txt
	"""
	return join(get_current_path(), 'keyFiles', 
				'keys_' + datetime.today().strftime('%Y%m%d') + '.txt')



if __name__ == '__main__':
	from blp_trade.utility import get_current_path
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	# writeXMLFile(
	# 	filterTrades(
	# 		addRemoveHeader(
	# 			fileToLines(
	# 				join(get_current_path()
	# 					, 'samples'
	# 					, 'TransToGeneva20181031_morning.xml'
	# 				)
	# 			)
	# 		)
	# 		, loadKeys()
	# 	)
	# 	, 'output.xml'
	# )


	writeXMLFile(
		filterTrades(
			addRemoveHeader(
				fileToLines(
					join(get_current_path()
						, 'samples'
						, 'TransToGeneva20181031_night.xml'
					)
				)
			)
			, loadKeys()
		)
		, 'output2.xml'
	)