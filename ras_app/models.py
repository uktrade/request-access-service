from django.db import models
import uuid


class Approver(models.Model):
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    email = models.EmailField()

    def __str__(self):
        return self.email


class Services(models.Model):
    service_name = models.CharField(max_length=60)
    service_url = models.URLField(blank=True)
    service_docs = models.URLField(blank=True)

    def __str__(self):
        return self.service_name


class Teams(models.Model):
    team_name = models.CharField(max_length=60)
    sc = models.BooleanField(default=False)


class Request(models.Model):
    requestor = models.EmailField()
    approver = models.ForeignKey(Approver, on_delete=models.CASCADE)
    signed_off = models.BooleanField(default=False)
    signed_off_on = models.DateTimeField(null=True)
    reason = models.CharField(default=False, max_length=400)
    user_email = models.EmailField()
    completed = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    rejected_reason = models.CharField(blank=True, max_length=400)

    def add_request_items(self, service_ids):
        for service_id in service_ids:
            RequestItem.objects.create(request=self, services=Services.objects.get(id=service_id))

    def __str__(self):
        return str(self.id)


class RequestItem(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    services = models.ForeignKey(Services, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    additional_info = models.CharField(max_length=60, blank=True)


class User(models.Model):
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    email = models.EmailField(max_length=60)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    request = models.ForeignKey(Request, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.email


class RequestorDetails(models.Model):
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    email = models.EmailField(max_length=60)

    def __str__(self):
        return self.email


class AccountsCreator(models.Model):
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(blank=True, max_length=60)
    email = models.EmailField()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    services = models.ManyToManyField(Services)
