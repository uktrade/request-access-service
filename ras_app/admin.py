from django.contrib import admin

from .models import Approver, Services, User, Request, RequestItem, AccountsCreator, Teams
# Register your models here.


@admin.register(Approver)
class approver_admin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email')


@admin.register(Services)
class service_admin(admin.ModelAdmin):
    list_display = ('id', 'service_name', 'service_docs', 'service_url')


@admin.register(User)
class User_admin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'get_team', 'email', 'request', 'get_services')

    def get_services(self, obj):
        user = Request.objects.values_list('id', flat=True).filter(user_email=obj.email)
        service_accessible = RequestItem.objects.values_list(
            'services__service_name', flat=True).filter(request_id__in=user, completed=True)
        service_a_name = []
        for x in service_accessible:
            service_a_name.append(x)
        return service_a_name

    def requests_submitted(self, obj):
        return str(obj.request.id)

    def get_team(self, obj):
        return (obj.team.team_name)


@admin.register(AccountsCreator)
class AccountsCreator_admin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'get_services', 'uuid')
    filter_horizontal = ('services',)

    def get_services(self, obj):
        return "\n".join([p.service_name for p in obj.services.all()])


@admin.register(Teams)
class teams_admin(admin.ModelAdmin):
    list_display = ('id', 'team_name')
