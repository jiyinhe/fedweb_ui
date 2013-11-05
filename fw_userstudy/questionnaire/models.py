from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
	user = models.ForeignKey(User)
	IP = models.IPAddressField()
	# Basic info
	GENDER = (('F', 'Female'), ('M', 'Male'))
	gender = models.CharField(max_length=1, choices=GENDER) 
	year_of_birth = models.IntegerField() 

	# Skills
	PROF = ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5))
	computer_exp = models.IntegerField(choices=PROF)
	english_exp = models.IntegerField(choices=PROF)
	search_exp = models.IntegerField(choices=PROF)	
	
	# Education
	EL = (('H', 'Highschool'), ('U', 'University'), ('M', 'Master'), ('D', 'Doctorate'))
	education = models.CharField(max_length=1, choices=EL)	
