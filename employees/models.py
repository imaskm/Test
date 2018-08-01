from django.db import models
from django import forms
from django.contrib import admin
from django.contrib.auth.models import User

class EmployeeOfficial(models.Model):
    user                = models.OneToOneField(User,on_delete=models.CASCADE,primary_key = True,related_name = "official_data")
    employee_id         = models.CharField(max_length = 7,unique=True,null=False)
    team                = models.CharField(max_length = 30,null =True ,blank=True)
    designation         = models.CharField(max_length = 40,null=True ,blank=True)
    manager             = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank = True,related_name='manager')
    skills              = models.CharField(max_length = 100,null=True,blank=True)
    location            = models.CharField(max_length = 20, blank=True,null=True)
    is_current_employee = models.BooleanField(default = True)

    def __str__(self):
        return str(self.employee_id)

class Vehicle(models.Model):
    vehicle_number = models.CharField(max_length = 10 , unique = True)
    VEHICLE_TYPES  = (
                ('2','Two Wheeler'),
                ('4','Four Wheeler'),
            )
    vehicle_type  = models.CharField(max_length = 1, choices = VEHICLE_TYPES)
    employee      = models.ForeignKey('Employee',on_delete=models.CASCADE,related_name = 'vehicles',null=False,blank=False)
    
    def __str__(self):
        return str(self.vehicle_type)+"  "+str(self.employee.user.username )

class Employee(models.Model):
    user              = models.OneToOneField(User,on_delete=models.CASCADE,primary_key = True,related_name='personal_data')
    mobile            = models.PositiveIntegerField(null=True)
    email_alternate   = models.EmailField('Alternate Email ID',null=True)
    mobile_emergency  = models.PositiveIntegerField('Emergency Contact Number',null=True)
    address           = models.CharField(max_length = 250,null=True)
    BLOOD_GROUPS = (
                ('O+','O+'),
                ('A+','A+'),
                ('B+','B+'),
                ('AB+','AB+'),
                ('O-','O-'),
                ('A-','A-'),
                ('B-','B-'),
                ('AB-','AB-'),
        )
    blood_group       = models.CharField(max_length = 3,choices=BLOOD_GROUPS,default = None,null=True,blank=True )

    def __str__(self):
        return str(self.user)









