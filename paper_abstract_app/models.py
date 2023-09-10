from django.db import models


class Journal(models.Model):
    name = models.CharField(max_length=200)
    impact_factor = models.FloatField(default=0.0)

    def __str__(self):
        return self.name

class Articlemodel(models.Model):

    PMID = models.IntegerField(null=True)
    Date_publish = models.CharField(max_length=200)
    Title = models.CharField(max_length=200)
    Author = models.CharField(null=True , max_length=200)
    Abstract = models.TextField()
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE)
    DOI = models.URLField(null=True)
    
    def __str__(self):
        return self.Title


