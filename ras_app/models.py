from django.db import models
import uuid

# Create your models here.
class Approver(models.Model):
    firstname = models.CharField(max_length=60)
    surname = models.CharField(max_length=60)
    email = models.EmailField()

    def __str__(self):
        return self.email

class Services(models.Model):
    service_name = models.CharField(max_length=60)

    def __str__(self):
        return self.service_name

class Request(models.Model):
    requestor = models.EmailField()
    approver = models.ForeignKey(Approver, on_delete=models.CASCADE)
    #services = models.ManyToManyField(Services)#, through='RequestServices')
    signed_off = models.BooleanField(default=False)
    signed_off_on = models.DateTimeField(null=True)
    reason = models.CharField(max_length=400)
    user_email = models.EmailField()
    token = models.CharField(default=False, max_length=20)
    completed = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    rejected_reason = models.CharField(blank=True, max_length=400)

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

class User(models.Model):
    firstname = models.CharField(max_length=60)
    surname = models.CharField(max_length=60)
    email = models.EmailField(max_length=60)#, unique=True)
    end_date = models.DateField(null=True)
    request = models.ForeignKey(Request, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.email

class RequestorDetails(models.Model):
    firstname = models.CharField(max_length=60)
    surname = models.CharField(max_length=60)
    email = models.EmailField(max_length=60)#, unique=True)
    #request = models.ForeignKey(Request, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.email

class AccountsCreator(models.Model):
    firstname = models.CharField(max_length=60)
    surname = models.CharField(blank=True, max_length=60)
    email = models.EmailField()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    services = models.ManyToManyField(Services)

# class RequestServices(models.Model):
#     request = models.ForeignKey(Request, on_delete=models.CASCADE)
#     service = models.ForeignKey(Services, on_delete=models.CASCADE)
#     completed = models.BooleanField(default=False)
#     completed_date = models.DateTimeField(null=True)
