from django.db import models
from django.contrib.auth.models import User
from django.core import validators

class Person(models.Model):
    FirstName = models.CharField(max_length=255)
    Prefix = models.CharField(max_length=255, null=True, blank=True)
    LastName = models.CharField(max_length=255)

    def __str__(self):
        if self.Prefix is not None:
            return '{} {} {}'.format(str(self.FirstName).capitalize(), self.Prefix, str(self.LastName).capitalize())
        else:
            return '{} {}'.format(str(self.FirstName).capitalize(), str(self.LastName).capitalize())

    class Meta:
        ordering = ['LastName']

class SubDance(models.Model):
    Name = models.CharField(max_length=255)
    def __str__(self):
        return self.Name

    class Meta:
        ordering = ('dancesubdancerelation',)


class Dance(models.Model):
    Name = models.CharField(max_length=255)
    Jury = models.ManyToManyField(User, related_name='jury', blank=True)
    SubDances = models.ManyToManyField(SubDance, related_name='dances', through='DanceSubDanceRelation')

    def __str__(self):
        return self.Name

class DanceSubDanceRelation(models.Model):
    Dance = models.ForeignKey(Dance, on_delete=models.CASCADE)
    SubDance = models.ForeignKey(SubDance, on_delete=models.CASCADE)
    Order = models.IntegerField(validators=[validators.MinValueValidator(1)])

    def __str__(self):
        return str(self.SubDance) + ' for ' + str(self.Dance)

    class Meta:
        ordering = ('Order',)

class Pair(models.Model):
    BackNumber = models.IntegerField()
    LeadingRole = models.ForeignKey(Person, related_name='pairs_leading')
    FollowingRole = models.ForeignKey(Person, related_name='pairs_following')
    Dances = models.ManyToManyField(Dance, related_name='pairs')

    def __str__(self):
        return '{} with {}'.format(self.LeadingRole, self.FollowingRole)

    class Meta:
        ordering = ['LeadingRole']

class Grade(models.Model):
    Pair = models.ForeignKey(Pair, on_delete=models.CASCADE, related_name='grades')
    Dance = models.ForeignKey(Dance, on_delete=models.CASCADE, related_name='grades')
    Person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='grades')
    Jury = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')
    SubDance = models.ForeignKey(SubDance, on_delete=models.CASCADE, related_name='grades')

    Grade = models.DecimalField(max_digits=3, decimal_places=1)

    def __str__(self):
        return '{} for pair {} for dance {}'.format(self.Grade, self.Pair.id, self.SubDance)

class Heat(models.Model):
    Dance = models.ForeignKey(Dance, on_delete=models.CASCADE, related_name='heats')
    Persons = models.ManyToManyField(Pair, related_name='heats', blank=True)
    Number = models.IntegerField(validators=[validators.MinValueValidator(0)])

    def short_str(self):
        return "Heat {}".format(self.Number)

    def __str__(self):
        return "Heat {} for Dance {}".format(self.Number, self.Dance)

class MissingBackNumber(models.Model):
    Number = models.IntegerField(validators=[validators.MinValueValidator(1)], unique=True)

    def __str__(self):
        return str(self.Number)