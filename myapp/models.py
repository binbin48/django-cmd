from django.db import models


class Ticket(models.Model):
    token = models.CharField(max_length=36)
