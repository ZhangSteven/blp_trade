# blp_trade
Extract trades from Bloomberg's XML file, then create a new XML file with the
extracted trades and upload it to SFTP server.


# ver 0.2, 2019-01-31
Changes:

1. Now both trades and trade deletions for the particular portfolio (40006) are stored. Therefore if you make deletions for 40006 trades on AIM and this program is able to flow those deletions to Geneva, which is not available in previous version.

2. Instead of using a text file, a MySQL database on ubuntu-server01 is used to store the trade key values and mark whether those trades were deleted.



# ver 0.1, 2018-11-28
Extract trades from an XML file of the right portfolio, create a new XML file with the extracted trades and upload the output file to the SFTP server (in production mode only).


NOTE: 

(1) After extracting trades from a trade file, subsequent calls to the extraction function will not retrieve trades that have been extracted (saved into the key file keys_yyyymmdd.txt). 

(2) Trade cancellations won't be extracted because those transactions don't have the <Portfolio> tag.
