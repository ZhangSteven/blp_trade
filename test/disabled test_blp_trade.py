# coding=utf-8
# 

import unittest2
from os.path import join
from blp_trade.utility import get_current_path
from blp_trade.blp import deleteKeyFile, extractTradesToXML, fileToLines, \
                            addRemoveHeader, loadKeys



class TestBlpTrade(unittest2.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestBlpTrade, self).__init__(*args, **kwargs)

    @classmethod
    def setUp(cls):
        deleteKeyFile()

    @classmethod
    def tearDown(cls):
        deleteKeyFile()



    def testTradeXML(self):
        inputFile = join(get_current_path(), 'samples', 'TransToGeneva20181031_morning.xml')
        outputFile = join(get_current_path(), 'output.xml')
        extractTradesToXML(inputFile, outputFile)
        self.assertEqual(loadKeys(), ['1232542018', '124351'])

        inputFile2 = join(get_current_path(), 'samples', 'TransToGeneva20181031_night.xml')
        extractTradesToXML(inputFile2, outputFile)

        # this time, the output file should contain only one trade. Therefore,
        # if we delete the key file, which means all trades will be extracted,
        # we should still see just one trade.
        deleteKeyFile()
        extractTradesToXML(outputFile, 'test.xml')
        self.assertEqual(loadKeys(), ['124357'])