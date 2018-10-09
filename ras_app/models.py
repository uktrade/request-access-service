from django.db import models

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
    services = models.ManyToManyField(Services)
    signed_off = models.BooleanField(default=False)
    signed_off_on = models.DateTimeField(null=True)
    reason = models.CharField(max_length=400)
    user_email = models.EmailField()
    token = models.CharField(default=False, max_length=20)
    completed = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    rejected_reason = models.CharField(blank=True, max_length=400)

    def __str__(self):
        return str(self.id)

class User(models.Model):
    firstname = models.CharField(max_length=60)
    surname = models.CharField(max_length=60)
    email = models.EmailField(max_length=60)#, unique=True)
    end_date = models.DateField(null=True)
    #request = models.ManyToManyField(Request)
    request = models.ForeignKey(Request, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.email
