from os import path 

def prevent_overwrite(filename):
	"""Raises a FileExistsError if filename already exists

	Inputs:
		filename: the path to the file to check
	"""
	if path.exists(filename):
		raise FileExistsError('This file already exists: ' + filename +
				'\nAborting to prevent overwrite')
