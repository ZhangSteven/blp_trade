# coding=utf-8
# 

import unittest2
from os.path import join
from blp_trade.utility import get_current_path
from blp_trade.blp import deleteKeyFile, extractTradesToXML, fileToLines, \
                            addRemoveHeader, loadKeys



class TestBlp(unittest2.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestBlp, self).__init__(*args, **kwargs)

    @classmethod
    def setUp(cls):
        """
        Before starting the tests, let's set database to test mode and
        clear its contents.
        """
        setDatabaseMode('test')
        clearTestDatabase()


    @classmethod
    def tearDown(cls):
        pass



    def testFile1(self):
        inputFile = join(get_current_path(), 'samples', 'test1.xml')
        outputFile = join(get_current_path(), 'samples', 'output_test1.xml')

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