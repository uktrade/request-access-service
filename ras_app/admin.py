from django.contrib import admin

from .models import Approver, Services, User, Request
# Register your models here.

@admin.register(Approver)
class approver_admin(admin.ModelAdmin):
	list_display = ('firstname', 'surname', 'email')

@admin.register(Services)
class service_admin(admin.ModelAdmin):
	list_display = ('id', 'service_name')

@admin.register(Request)
class Request_admin(admin.ModelAdmin):
	list_display = ('requestor', 'approver', 'completed', 'signed_off', 'signed_off_on', 'reason', 'user_email', 'get_services')
	list_filter = ('signed_off', 'completed')
	filter_horizontal = ('services',)

	def approver(self, obj):
		return obj.approver.email,

	def services_approved(self, obj):
		return obj.services.service_name

	def get_services(self, obj):
		return "\n".join([p.service_name for p in obj.services.all()])


@admin.register(User)
class User_admin(admin.ModelAdmin):
	list_display = ('firstname', 'surname', 'email', 'end_date', 'request')
	#filter_horizontal = ('request',)

	# def approver(self, obj):
	# 	return obj.approver.email,

	def requests_submitted(self, obj):
		return str(obj.request.id)

	# def get_requests(self, obj):
	# 	return "\n".join([str(p.id) for p in obj.request.all()])
