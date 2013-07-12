from django.contrib import admin
from harvest_report.models import *

def set_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)
set_inactive.short_description = "Set Inactive"

def set_active(modeladmin, request, queryset):
    queryset.update(is_active=True)
set_active.short_description = "Set Active"



class EmployeeAdmin(admin.ModelAdmin):
	list_display = ['employee_id', 'first_name', 'last_name', 'is_active']
	list_filter = ['is_active']
	ordering = ['last_name']
	actions = [set_inactive, set_active]

class ClientAdmin(admin.ModelAdmin):
	list_display = ['client_id', 'client_name']
	ordering = ['client_name']

class AssignedTeam(admin.TabularInline):
	model = ProjectTeam

class ProjectAdmin(admin.ModelAdmin):
	list_display = ['client', 'project_name', 'is_active']
	list_filter = ['is_active']
	ordering = ['client']
	actions = [set_inactive, set_active]
	inlines = [AssignedTeam]

class TeamMembers(admin.TabularInline):
	model = EmployeeTeam

class TeamAdmin(admin.ModelAdmin):
	list_display = ['team_name', 'group_name']
	inlines = [TeamMembers]


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Team, TeamAdmin)
#admin.site.register(EmployeeTeam)
#admin.site.register(ProjectTeam)
admin.site.register(Booking)
admin.site.register(ProjectUpdate)
admin.site.register(ProjectWeekly)
admin.site.register(EmployeeProjectWeekly)

