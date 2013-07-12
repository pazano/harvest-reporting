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


class Index(tornado.web.RequestHandler):


	def get(self):
		self.render("index.html")


class Update(tornado.web.RequestHandler):

	def get(self):

		self.render("database_update.html")


class ShowEmployees(tornado.web.RequestHandler):

	def get(self):
		database = create_database("sqlite:report-three.db")
		store = Store(database)
		list_employees = store.find(Employee).order_by(Employee.last_name)

		self.render("show_employees.html", employees=list_employees)


class ShowClients(tornado.web.RequestHandler):

	def get(self):
		database = create_database("sqlite:report-three.db")
		store = Store(database)
		list_clients = store.find(Client).order_by(Client.client_name)

		self.render("show_clients.html", clients=list_clients)

class ShowProjects(tornado.web.RequestHandler):

	def get(self):
		database = create_database("sqlite:report-three.db")
		store = Store(database)
		raw_projects = store.find(Project).order_by(Project.client_id)
		cleaned_projects = []
		
		for row in raw_projects:
			client = store.find(Client, Client.client_id==row.client_id).one()
			cleaned_projects.append({
				'project_id' : row.project_id,
				'client' : client.client_name,
				'project' : row.project_name
				})

		self.render("show_projects.html", display='all', projects=cleaned_projects)

class ShowWeeklyBookings(tornado.web.RequestHandler):

	def get(self):
		date = self.get_argument('d', False)
		database = create_database("sqlite:report-three.db")
		store = Store(database)
		print("Rendering weekly bookings, date=" + str(date))
		
		query_week = int()

		if date is not False:
# Should validate that it is a six-digit number somehow
			date = str(date)
			year = int(date[:4])
			month = int(date[4:6])
			day = int(date[6:8])
			date_obj = datetime.date(year, month, day)
			date_week = date_obj - datetime.timedelta(days=date_obj.weekday())
			date_week = datetimeInt(date_week)
			query_week = date_week
			
		else:
			query_week = store.find(Max(Booking.week_of)).one()
		
		display_week = str(query_week)
		display_week = display_week[4:6] + '/' + display_week[6:8] + '/' + display_week[:4]
		
		this_week = store.find(Booking, Booking.week_of==query_week)
		self.render("show_bookings.html", bookings=this_week, week_of=display_week)


class WeeklyReport(tornado.web.RequestHandler):

	def get(self):
		database = create_database("sqlite:report-three.db")
		store = Store(database)

		# URL Queries it cares about
		display_type = self.get_argument('type', None)
		content_id = int(self.get_argument('id', 1)) # Later on, this should default to an employee / team / project list view
		week_of = self.get_argument('week', None)
		
		fallback_week = store.find(Max(EmployeeWeekly.week_of)).one()

		# Ghetto Verify:  Fallback if week is not provided, and check if it is a six digit number
		if week_of is not None and len(str(int(week_of))) is not 8:
			week_of = fallback_week
		elif week_of is None:
			week_of = fallback_week
		else:
			week_of = int(week_of)
		
		# And just in case, make sure it doesn't exceed the last week_of in the report table
		if week_of > fallback_week:
			week_of = fallback_week

		
		# Ghetto Verify pt 2:  Make sure date is a Monday, for Query purposes
		week_str = str(week_of)
		week_date = intDatetime(week_of)
		week_date = week_date - datetime.timedelta(days=week_date.weekday()) # Sets day to Monday
		week_of = datetimeInt(week_date)
		

		week_display = week_str[4:6] + ' / ' + week_str[6:8] + ' / ' + week_str[:4]


#########
		# Single Employee View
		if display_type == 'employee':
			
			

			self.render("report_weekly.html", view=display_type, name=employee_name, records=list_totals, week_of=week_display)

#########
		# Team Report View
		elif display_type == 'team':


			# Team Report Data (top of page)
			team_list = Select(EmployeeTeam.employee_id, And(EmployeeTeam.team_id==content_id, EmployeeTeam.active_from < week_of, EmployeeTeam.active_to > week_of))
			team_bookings = store.find(EmployeeWeekly, EmployeeWeekly.employee_id.is_in(team_list), EmployeeWeekly.week_of==week_of).order_by(EmployeeWeekly.full_name)

			team_name = store.find(Team.team_name, Team.team_id==content_id).one()
			team_name = str(team_name)

			
			# Prep Project Data
			project_ids = store.find(ProjectTeam.project_id, And(ProjectTeam.team_id==content_id, ProjectTeam.active_from < week_of, ProjectTeam.active_to > week_of))
			project_set = []

			for project in project_ids:
				project_name = store.find(Project.project_name, Project.project_id==project).one()
				project_start = store.find(ProjectTeam.active_from, And(ProjectTeam.project_id==project, ProjectTeam.team_id==content_id)).one()
				billable_sum = store.find(Sum(EmployeeProjectWeekly.billable_total), And(EmployeeProjectWeekly.project_id==project, EmployeeProjectWeekly.week_of==week_of)).one()
				
				dollar_amount = "$0"
				if billable_sum is not None:
					dollar_amount = "${0:.0f}".format(billable_sum * 160)

				project_total = store.find(Sum(EmployeeProjectWeekly.billable_total), And(EmployeeProjectWeekly.project_id==project, EmployeeProjectWeekly.week_of >= project_start, EmployeeProjectWeekly.week_of <= week_of)).one()
				project_total_nonbill = store.find(Sum(EmployeeProjectWeekly.nonbill_total), And(EmployeeProjectWeekly.project_id==project, EmployeeProjectWeekly.week_of >= project_start, EmployeeProjectWeekly.week_of <= week_of)).one()
				
				project_total_dollars = "$0"
			
				if project_total is not None:
					project_total_dollars = "${0:.0f}".format(project_total * 160)

				# Detailed Employee Billings Per Project for the Week
				project_employee_bookings = store.find(EmployeeProjectWeekly, And(EmployeeProjectWeekly.project_id==project, EmployeeProjectWeekly.week_of==week_of)).order_by(EmployeeProjectWeekly.full_name)
				project_employee_set = []
				for employee_booking in project_employee_bookings: 

					project_employee_total = store.find(Sum(EmployeeProjectWeekly.billable_total), And(EmployeeProjectWeekly.project_id==project, EmployeeProjectWeekly.employee_id==employee_booking.employee_id, EmployeeProjectWeekly.week_of >= project_start, EmployeeProjectWeekly.week_of <= week_of)).one()
					project_employee_set.append({
						"name" : employee_booking.full_name,
						"weekly_hours" : employee_booking.billable_total,
						"nonbill_hours" : employee_booking.nonbill_total,
						"total_hours" : project_employee_total
						})


				project_set.append({
					"project_name" : project_name,
					"billable_hours" : billable_sum,
					"nonbill_hours" : project_total_nonbill,
					"dollar_amount" : dollar_amount, 
					"project_total" : project_total_dollars,
					"bookings" : project_employee_set
				})
				
			
			# Prep Navigation Links
			week_of_date = intDatetime(week_of)
			next_week = week_of_date - datetime.timedelta(days=-7)
			prev_week = week_of_date - datetime.timedelta(days=7)

			max_week = store.find(Max(EmployeeProjectWeekly.week_of)).one()

			prev_qs = { 'type' : 'team', 'id' : content_id, 'week' : datetimeInt(prev_week)}
			next_qs = { 'type' : 'team', 'id' : content_id, 'week' : datetimeInt(next_week)}
			max_qs = { 'type' : 'team', 'id' : content_id, 'week' : max_week}

			prev_link = '/weekly-report?' + urllib.urlencode(prev_qs)
			next_link = '/weekly-report?' + urllib.urlencode(next_qs)
			max_link = '/weekly-report?' + urllib.urlencode(max_qs)



			self.render("report_weekly.html", view=display_type, name=team_name, records=team_bookings, projects=project_set, week_of=week_display, next=next_link, prev=prev_link, max=max_link)

#########		
		# Project Report View
		elif display_type == 'project':

			# Weekly Bookings for this Project
			project_bookings = store.find()

			self.render("report_weekly.html", view=display_type, records=list_totals, week_of=week_display)

		# Default View.  Show Person or Project Selections
		else:

			self.render("report_weekly.html", view='default')
		


		
