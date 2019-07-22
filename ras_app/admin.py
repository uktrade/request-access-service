from django.contrib import admin

from .models import Approver, Services, User, Request, RequestItem, AccountsCreator, Teams
# Register your models here.

@admin.register(Approver)
class approver_admin(admin.ModelAdmin):
	list_display = ('firstname', 'surname', 'email')

@admin.register(Services)
class service_admin(admin.ModelAdmin):
	list_display = ('id', 'service_name', 'service_docs', 'service_url')

# @admin.register(Request)
# class Request_admin(admin.ModelAdmin):
# 	list_display = ('requestor', 'approver', 'completed', 'signed_off', 'signed_off_on', 'reason', 'user_email', 'get_services', 'token')
# 	list_filter = ('signed_off', 'completed')
# 	#filter_horizontal = ('services',)
#
# 	def approver(self, obj):
# 		return obj.approver.email,
#
# 	# def services_approved(self, obj):
# 	# 	return obj.services.service_name
#
# 	def get_services(self, obj):
# 		return "\n".join([p.service_name for p in obj.services.all()])


@admin.register(User)
class User_admin(admin.ModelAdmin):
	list_display = ('firstname', 'surname', 'get_team', 'email', 'request', 'get_services')
	#list_display = ('firstname', 'surname', 'get_team', 'email', 'end_date', 'request', 'get_services')
	#filter_horizontal = ('request',)
	def get_services(self, obj):
		#import pdb; pdb.set_trace()
		user = Request.objects.values_list('id', flat=True).filter(user_email=obj.email)
		service_accessible = RequestItem.objects.values_list('services__service_name', flat=True).filter(request_id__in=user, completed=True)
		service_a_name = []
		for x in service_accessible:
			service_a_name.append(x)
		return service_a_name
	# def approver(self, obj):
	# 	return obj.approver.email,

	def requests_submitted(self, obj):
		return str(obj.request.id)

	def get_team(self, obj):
		return (obj.team.team_name)

	# def get_requests(self, obj):
	# 	return "\n".join([str(p.id) for p in obj.request.all()])

@admin.register(AccountsCreator)
class AccountsCreator_admin(admin.ModelAdmin):
	list_display = ('firstname', 'surname', 'email', 'get_services', 'uuid')
	filter_horizontal = ('services',)

	def get_services(self, obj):
		return "\n".join([p.service_name for p in obj.services.all()])

@admin.register(Teams)
class teams_admin(admin.ModelAdmin):
	list_display = ('id', 'team_name')
