import tornado.httpserver, tornado.ioloop, tornado.options, tornado.web, os.path, random, string
import tornado.httpclient as httpclient
import logging
import datetime
from routes.data import *
from storm.locals import *
from storm.expr import Sum
from tornado.options import define, options


class EmployeeWeeklyData(tornado.web.RequestHandler):

	def get(self):

		database = create_database("sqlite:report-three.db")
		store = Store(database)

		# Get all unique IDs
		emp_sub = Select(Booking.employee_id, distinct=True)
		week_sub = Select(Booking.week_of, distinct=True)
		
		employee_bulk = store.find(Booking.employee_id).order_by(Booking.employee_id)
		week_bulk = store.find(Booking.week_of).order_by(Booking.week_of)
		#week_set = store.find(Booking.week_of, distinct=True).order_by(Booking.week_of)

		week_set = set()
		employee_set = set()

		for week in week_bulk:
			week_set.add(week)
		for employee in employee_bulk:
			employee_set.add(employee)

		print(week_set)
		print(employee_set)
		

		for week in week_set:
			
			
			for employee in employee_set:
				
				booking_exists = store.find(Booking, And(Booking.employee_id==employee, Booking.week_of==week))
				if booking_exists.count() != 0:
					
					billable_sum = store.find( Sum(Booking.billable_total), And(Booking.employee_id==employee, Booking.week_of==week)).one()
					nonbill_sum = store.find( Sum(Booking.nonbill_total), And(Booking.employee_id==employee, Booking.week_of==week)).one()
					exception_sum = store.find( Sum(Booking.exception_total), And(Booking.employee_id==employee, Booking.week_of==week)).one()
					pto_sum = store.find( Sum(Booking.pto_total), And(Booking.employee_id==employee, Booking.week_of==week)).one()

					# Look for an existing employee / weekly for this date
					status_exists = store.find(EmployeeWeekly, EmployeeWeekly.employee_id==employee, EmployeeWeekly.week_of==week)

					# Create New Record if it does
					if status_exists.count() == 0:
						
						employee_name = store.find(Employee.full_name, Employee.employee_id==employee).one()

						ew_record = EmployeeWeekly()
						ew_record.employee_id = employee
						ew_record.full_name = employee_name
						ew_record.week_of = week
						ew_record.billable_total = float(billable_sum)
						ew_record.nonbill_total = float(nonbill_sum)
						ew_record.exception_total = float(exception_sum)
						ew_record.pto_total = float(pto_sum)
						store.add(ew_record)

						print('Add new, ' + str(ew_record.full_name) + ' week_of=' + str(week) + ", " + str(ew_record.billable_total))

					else:
						update_record = store.find(EmployeeWeekly, EmployeeWeekly.employee_id==employee, EmployeeWeekly.week_of==week).one()
						update_record.billable_total = billable_sum
						update_record.nonbill_total = nonbill_sum
						update_record.exception_total = exception_sum
						update_record.pto_total = pto_sum

						print('Update, ' + str(update_record.full_name) + ' week_of=' + str(week))				

					store.flush()
						
				else:
					skipped_name = store.find(Employee.full_name, Employee.employee_id==employee).one()
					print("No Bookings for " + str(skipped_name) + " the week of " + str(week) )

		store.commit()	
		self.render("report_refresh.html")



class ProjectWeeklyData(tornado.web.RequestHandler):

	def get(self):

		database = create_database("sqlite:report-three.db")
		store = Store(database)

		# Get all unique IDs
	
		project_bulk = store.find(Booking.project_id).order_by(Booking.project_id)
		week_bulk = store.find(Booking.week_of).order_by(Booking.week_of)

		project_set = set()
		week_set = set()
		employee_set = set()

		for week in week_bulk:
			week_set.add(week)
		for project in project_bulk:
			project_set.add(project)

		employee_bulk = store.find(Booking.employee_id, And(Booking.week_of.is_in(week_set), Booking.project_id.is_in(project_bulk)))

		for employee in employee_bulk:
			employee_set.add(employee)
	

		for week in week_set:
			
			# Update Project Status values for this week
			for project in project_set:
				

				billable_sum = store.find( Sum(Booking.billable_total), And(Booking.project_id==project, Booking.week_of==week)).one()
				nonbill_sum = store.find( Sum(Booking.nonbill_total), And(Booking.project_id==project, Booking.week_of==week)).one()

				# Look for an existing Project Weekly totals record
				status_exists = store.find(ProjectWeekly, And(ProjectWeekly.project_id==project, ProjectWeekly.week_of==week))

				# Create Record if none is found
				if status_exists.count() == 0:
					new_record = ProjectWeekly();
					new_record.project_id = project
					new_record.week_of = week
					new_record.billable_total = billable_sum
					new_record.nonbill_total = nonbill_sum
					store.add(new_record)
					print('Creating New Project Weekly for id=' + str(project) + ' week_of=' + str(week))					

				# Update Existing Values if one is found
				else:
					update_record = store.find(ProjectWeekly, And(ProjectWeekly.project_id==project, ProjectWeekly.week_of==week)).one()
					update_record.billable_total = billable_sum
					update_record.nonbill_total = nonbill_sum
					print('Updating Project Weekly for id=' + str(project) + '  & week_of=' + str(week))
				
				store.flush();
				store.commit();



				# Update all Employee totals for this project
				for employee in employee_set:
					
					booking_exists = store.find(Booking, And(Booking.project_id==project, Booking.week_of==week, Booking.employee_id==employee))
					
					if booking_exists.count() != 0:
						
						billable_sum = store.find( Sum(Booking.billable_total), And(Booking.project_id==project, Booking.week_of==week, Booking.employee_id==employee)).one()
						nonbill_sum = store.find( Sum(Booking.nonbill_total), And(Booking.project_id==project, Booking.week_of==week, Booking.employee_id==employee)).one()
						exception_sum = store.find( Sum(Booking.exception_total), And(Booking.project_id==project, Booking.week_of==week, Booking.employee_id==employee)).one()

						# Look for an existing employee / project / weekly for this date
						status_exists = store.find(EmployeeProjectWeekly, And(EmployeeProjectWeekly.project_id==project, EmployeeProjectWeekly.employee_id==employee, EmployeeProjectWeekly.week_of==week))

						# Create New Record if it does
						if status_exists.count() == 0:
							
							employee_name = store.find(Employee.full_name, Employee.employee_id==employee).one()
							project_name = store.find(Project.project_name, Project.project_id==project).one()

							print(str(employee_name))
							print(employee_name)

							ew_record = EmployeeProjectWeekly()
							ew_record.employee_id = employee
							ew_record.full_name = unicode(employee_name)
							ew_record.project_id = project
							ew_record.week_of = week
							ew_record.billable_total = float(billable_sum)
							ew_record.nonbill_total = float(nonbill_sum)
							ew_record.exception_total = float(exception_sum)
							store.add(ew_record)

							#print('Add new, ' + str(project_name) + " - " + str(ew_record.full_name) + ' week_of=' + str(week) + ", " + str(ew_record.billable_total))

						else:
							update_record = store.find(EmployeeProjectWeekly, And(EmployeeProjectWeekly.project_id==project, EmployeeProjectWeekly.employee_id==employee, EmployeeProjectWeekly.week_of==week)).one()
							update_record.billable_total = billable_sum
							update_record.nonbill_total = nonbill_sum
							update_record.exception_total = exception_sum

							project_name = store.find(Project.project_name, Project.project_id==update_record.project_id).one()
							#print('Update, ' + str(project_name) + " - " + str(ew_record.full_name) + ' week_of=' + str(week) + ", " + str(ew_record.billable_total))				

						store.flush()
						store.commit()		
					else:
						skipped_name = store.find(Employee.full_name, Employee.employee_id==employee).one()
						project_name = store.find(Project.project_name, Project.project_id==project).one()

						#print("No Bookings for " + str(skipped_name) + " the week of " + str(week) + " on Project: " + str(project_name))

		self.render("report_refresh.html")


