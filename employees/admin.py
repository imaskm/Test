from django.contrib import admin
from django.contrib.auth.models import User
from .models import *

'''class AdminEmployee(admin.ModelAdmin):
    print('here_out') 
    def save_model(self,request,obj,form,change):
        print('here1234')
        return '123'
        obj.user='AshKau'
        return super().save_model(request,obj,form,change)
        print('Object',obj)
        print('Request',request)
        print('change',change)
'''

#admin.site.unregister(User)
#admin.site.register(User,AdminEmployee)

# Register your models here.
