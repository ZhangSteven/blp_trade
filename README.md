# blp_trade
Extract trades from Bloomberg's XML file, then create a new XML file with the
extracted trades and upload it to SFTP server.



# ver 0.1, 2018-11-28
Extract trades from an XML file of the right portfolio, create a new XML file with the extracted trades and upload the output file to the SFTP server (in production mode only).


NOTE: 

(1) After extracting trades from a trade file, subsequent calls to the extraction function will not retrieve trades that have been extracted (saved into the key file keys_yyyymmdd.txt). 

(2) Trade cancellations won't be extracted because those transactions don't have the <Portfolio> tag.