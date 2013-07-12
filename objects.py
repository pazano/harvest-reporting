#!/usr/bin/python

class Report(object):


	def __init__(self):
		self.root_url = "http://redinteractive.harvestapp.com"
		self.read_api(self.root_url)

	def read_api(self, url):
		print url


my_report = Report()
