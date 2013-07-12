import tornado.httpserver, tornado.ioloop, tornado.options, tornado.web, os.path, random, string
import tornado.httpclient as httpclient
import datetime
#import storm

from storm.locals import *


class Employee(object):
	__storm_table__ = "employees"
	employee_id = Int(primary=True)
	first_name = Unicode()
	last_name = Unicode()
	full_name = Unicode()
	role = Unicode()
	#team_id = Int()


class Client(object):
	__storm_table__ = "clients"
	client_id = Int(primary=True)
	client_name = Unicode()

class Project(object):
	__storm_table__ = "projects"
	project_id = Int(primary=True)
	client_id = Int()
	project_name = Unicode()
	is_active = Int()
	#sow_budget = Float()
#HELP?	
	#start_date = Unicode()
	#launch_date = Unicode()

class ProjectUpdate(object):
	__storm_table__ = "project_update"
	status_id = Int(primary=True)
	project_id = Int()
	date = Int()
	week_of = Int()
	total_budget = Float()
	notes = Pickle()


class ProjectWeekly(object):
	__storm_table__ = "project_weekly_total"
	status_id = Int(primary=True)
	project_id = Int()
	week_of = Int()
	billable_total = Float()
	nonbill_total = Float()

class ProjectTeam(object):
	__storm_table__ = "project_team"
	assign_id = Int(primary=True)
	project_id = Int()
	team_id = Int()
	active_from = Int()
	active_to = Int()

class Booking(object):
	__storm_table__ = "raw_bookings"
	booking_id = Int(primary=True)
	date = Int()
	week_of = Int()
	client_id = Int()
	project_id = Int()
	employee_id = Int()
	task_name = Unicode()
	billable_total = Float()
	nonbill_total = Float()
	exception_total = Float()
	pto_total = Float()

class EmployeeWeekly(object):
	__storm_table__ = "employee_weekly_total"
	status_id = Int(primary=True)
	employee_id = Int()
	full_name = Unicode()
	week_of = Int()
	billable_total = Float()
	nonbill_total = Float()
	exception_total = Float()
	pto_total = Float()

class EmployeeProjectWeekly(object):
	__storm_table__ = "employee_project_weekly"
	status_id = Int(primary=True)
	employee_id = Int()
	full_name = Unicode()
	project_id = Int()
	week_of = Int()
	billable_total = Float()
	nonbill_total = Float()
	exception_total = Float()

class Team(object):
	__storm_table__ = "teams"
	team_id = Int(primary=True)
	team_name = Unicode()
	group_name = Unicode()

class EmployeeTeam(object):
	__storm_table__ = "employee_team"
	assign_id = Int(primary=True)
	employee_id = Int()
	team_id = Int()
	active_from = Int()
	active_to = Int()