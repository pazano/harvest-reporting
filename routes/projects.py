import tornado.httpserver, tornado.ioloop, tornado.options, tornado.web, os.path, random, string
import tornado.httpclient as httpclient
import logging
import csv
import urllib
import datetime
from routes.data import *
from routes.reportfun import *
from storm.locals import *
from storm.expr import Sum
from tornado.options import define, options


class UpdateProjects(tornado.web.RequestHandler):

	def get(self):

		#Set up the array of projects, render the page in selection mode
		database = create_database("sqlite:report-three.db")
		store = Store(database)
		active_projects = store.find(Project, Project.is_active==1)

		self.render("update_project_form.html", view='select', projects=active_projects)

	def post(self):

		#Check to make sure a project and date was sent, otherwise kick back to the normal page
		project_id = self.get_argument('project', None)
		report_date = self.get_argument('date', None)

		#Success or failure, will still need a db connection and the full list of active projects
		database = create_database("sqlite:report-three.db")
		store = Store(database)
		active_projects = store.find(Project, Project.is_active==1)

		if project_id is not None and report_date is not None:

			#Check for an existing report
			report_exists = store.find(ProjectUpdate, And(ProjectUpdate.project_id==project_id, ProjectUpdate.date==report_date)).one()

			if report_exists is not None:
				print("this is inside the if checking if the report exists")

			self.render("update_project_form.html", view="edit", projects=active_projects, project=this_project, date="20130101")

		else:
			self.render("update_project_form.html", message="Post data was missing something", view="select", projects=active_projects)
