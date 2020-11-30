#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('requirements.txt', 'r') as reqs:
	requirements = reqs.readlines()

setup(name='boundless-middleware',
	version='1.0',
	description='middleware for boundless databases and interactions',
	author='Philip Bove',
	install_requires=requirements,
	author_email='phil@bove.online',
	packages=find_packages(),
	scripts=['bin/boundless']
)
