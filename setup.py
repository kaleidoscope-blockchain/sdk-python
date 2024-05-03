from setuptools import setup, find_packages

setup (
	name			= "witnesschain",
	version			= "0.1.4",
	author			= "arun",
	author_email		= "x@example.com",
	description		= "A short description of your package",
	packages		= find_packages(),
	install_requires	= ["requests"],
	classifiers		= [
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	url			= "https://github.com/kaleidoscope-blockchain/sdk-python",
	python_requires		= ">=3.6",
)
