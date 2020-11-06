from django.db import models


# Create your models here.
class ContentScoreModel(models.Model):
    id = models.CharField(max_length=50, unique=True, primary_key=True)
    category = models.CharField(max_length=30)
    level = models.CharField(max_length=30)
    newspubName = models.CharField(max_length=30)
    score = models.IntegerField()
    time = models.DateTimeField()
    rank = models.IntegerField(blank=True, null=True)
