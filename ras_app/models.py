from django.db import models
import uuid

# Create your models here.
class Approver(models.Model):
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    email = models.EmailField()

    def __str__(self):
        return self.email

class Services(models.Model):
    service_name = models.CharField(max_length=60)
    service_url = models.URLField(blank=True)
    service_docs =  models.URLField(blank=True)
    #additional_info = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return self.service_name

class Teams(models.Model):
    team_name = models.CharField(max_length=60)
    sc = models.BooleanField(default=False)

class Request(models.Model):
    requestor = models.EmailField()
    approver = models.ForeignKey(Approver, on_delete=models.CASCADE)
    #services = models.ManyToManyField(Services)#, through='RequestServices')
    signed_off = models.BooleanField(default=False)
    signed_off_on = models.DateTimeField(null=True)
    reason = models.CharField(default=False, max_length=400)
    user_email = models.EmailField()
    token = models.CharField(default=False, max_length=20)
    completed = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    rejected_reason = models.CharField(blank=True, max_length=400)
    #team = models.ForeignKey(Teams, on_delete=models.CASCADE)

    def add_request_items(self, service_ids):
        #import pdb; pdb.set_trace()
        for service_id in service_ids:
            RequestItem.objects.create(request=self, services=Services.objects.get(id=service_id))

    def __str__(self):
        return str(self.id)

class RequestItem(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    #services = models.OneToOneField(Services, on_delete=models.CASCADE)
    services = models.ForeignKey(Services, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    additional_info = models.CharField(max_length=60, blank=True)

class User(models.Model):
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    email = models.EmailField(max_length=60)#, unique=True)
    #end_date = models.DateField(null=True)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    request = models.ForeignKey(Request, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.email

class RequestorDetails(models.Model):
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    email = models.EmailField(max_length=60)#, unique=True)
    #request = models.ForeignKey(Request, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.email

class AccountsCreator(models.Model):
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(blank=True, max_length=60)
    email = models.EmailField()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    services = models.ManyToManyField(Services)


# class RequestServices(models.Model):
#     request = models.ForeignKey(Request, on_delete=models.CASCADE)
#     service = models.ForeignKey(Services, on_delete=models.CASCADE)
#     completed = models.BooleanField(default=False)
#     completed_date = models.DateTimeField(null=True)
