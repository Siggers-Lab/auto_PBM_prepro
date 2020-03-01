from os import path 
import logging

def prevent_overwrite(filename):
	"""Raises a FileExistsError if filename already exists

	Inputs:
		filename: the path to the file to check
	"""
	if path.exists(filename):
		logging.error('This file/directory already exists: ' +
				filename + '\nAborting to prevent overwrite')
		raise FileExistsError('This file/directory already exists: ' +
				filename + '\nAborting to prevent overwrite')
