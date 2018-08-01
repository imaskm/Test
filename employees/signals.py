from django.contrib.auth.models import User
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from .models import EmployeeOfficial,Employee,Vehicle

@receiver(post_save,sender=User)
def create_employee(sender,instance,created,**kwargs):

    if(created):
        try:
            pass
            #empoff_obj = EmployeeOfficial.objects.create(user = instance,employee_id = instance.username )
            #empoff_obj.save()
            #emp_obj    = Employee.objects.create(employee_id = empoff_obj.employee_id,user = instance )
            #emp_obj.save()
        except:
            raise Exception('Some Error Occured in Application')


@receiver(pre_save,sender=User)
def create_username(sender,instance,*args,**kwargs):
    instance.username   = instance.username.lower()
    instance.email      = instance.email.lower()
    #instance.first_name = instance.first_name.lower()
    #instance.last_name  = instance.last_name.lower()


