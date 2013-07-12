from django.db import models

class Employee(models.Model):
	employee_id = models.AutoField(primary_key=True)
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	full_name = models.CharField(max_length=150)
	role = models.CharField(max_length=150)
	is_active = models.BooleanField(default=False)

	def __unicode__(self):
		return self.full_name

class Client(models.Model):
	client_id = models.AutoField(primary_key=True)
	client_name = models.CharField(max_length=300)

	def __unicode__(self):
		return self.client_name

class Project(models.Model):
	project_id = models.AutoField(primary_key=True)
	client = models.ForeignKey('Client')
	project_name = models.CharField(max_length=300)
	is_active = models.BooleanField()

	def __unicode__(self):
		return self.project_name

class Team(models.Model):
	team_id = models.AutoField(primary_key=True)
	team_name = models.CharField(max_length=50)
	group_name = models.CharField(max_length=50)

	def __unicode__(self):
		return self.team_name

class EmployeeTeam(models.Model):
	assign_id = models.AutoField(primary_key=True)
	employee = models.ForeignKey('Employee')
	team = models.ForeignKey('Team')
	active_from = models.IntegerField(max_length=8)
	active_to = models.IntegerField(max_length=8)

class ProjectUpdate(models.Model):
	status_id = models.AutoField(primary_key=True)
	project = models.ForeignKey('Project')
	date = models.IntegerField(max_length=8)
	week_of = models.IntegerField(max_length=8)
	total_budget = models.FloatField()

class ProjectWeekly(models.Model):
	status_id = models.AutoField(primary_key=True)
	project = models.ForeignKey('Project')
	week_of = models.IntegerField(max_length=8)
	billable_total = models.FloatField()
	nonbill_total = models.FloatField()

class ProjectTeam(models.Model):
	assign_id = models.AutoField(primary_key=True)
	project = models.ForeignKey('Project')
	team = models.ForeignKey('Team')
	active_from = models.IntegerField(max_length=8)
	active_to = models.IntegerField(max_length=8)

class Booking(models.Model):
	booking_id = models.AutoField(primary_key=True)
	date = models.IntegerField(max_length=8)
	week_of = models.IntegerField(max_length=8)
	client = models.ForeignKey('Client')
	project = models.ForeignKey('Project')
	employee = models.ForeignKey('Employee')
	task_name = models.CharField(max_length=150)
	billable_total = models.FloatField()
	nonbill_total = models.FloatField()
	exception_total = models.FloatField()
	pto_total = models.FloatField()

class EmployeeWeekly(models.Model):
	status_id = models.AutoField(primary_key=True)
	employee = models.ForeignKey('Employee')
	full_name = models.CharField(max_length=150)
	week_of = models.IntegerField(max_length=8)
	billable_total = models.FloatField()
	nonbill_total = models.FloatField()
	exception_total = models.FloatField()
	pto_total = models.FloatField()

class EmployeeProjectWeekly(models.Model):
	status_id = models.AutoField(primary_key=True)
	employee = models.ForeignKey('Employee')
	full_name = models.CharField(max_length=150)
	project = models.ForeignKey('Project')
	week_of = models.IntegerField(max_length=8)
	billable_total = models.FloatField()
	nonbill_total = models.FloatField()
	exception_total = models.FloatField()



