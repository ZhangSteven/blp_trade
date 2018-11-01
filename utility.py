# coding=utf-8
# 

import os, configparser



def get_current_path():
	"""
	Get the absolute path to the directory where this module is in.

	This piece of code comes from:

	http://stackoverflow.com/questions/3430372/how-to-get-full-path-of-current-files-directory-in-python
	"""
	return os.path.dirname(os.path.abspath(__file__))



def _load_config(config_file='blp.config'):
	"""
	Read the config file, convert it to a config object.
	"""
	cfg = configparser.ConfigParser()
	cfg.read(config_file)
	return cfg



# initialized only once when this module is first imported by others
if not 'config' in globals():
	config = _load_config()



def get_input_directory():
	"""
	The directory where the input XML file resides.
	"""
	global config
	return config['input']['directory']



def get_portfolio_id():
	global config
	return config['input']['portfolio']



def getFtpConfig():
	"""
	Returns: [Dictionary] config, for FTP related configuration
	"""
	global config
	cfg = {}
	cfg['winscpPath'] = config['ftp']['winscpPath']
	cfg['timeout'] = int(config['ftp']['timeout'])
	cfg['scriptDir'] = config['ftp']['scriptDir']
	cfg['logDir'] = config['ftp']['logDir']
	cfg['user'] = config['ftp']['user']
	cfg['password'] = config['ftp']['password']
	cfg['server'] = config['ftp']['server']
	cfg['targetDir'] = config['ftp']['targetDir']
	return cfg