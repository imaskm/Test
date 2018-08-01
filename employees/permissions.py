from rest_framework import permissions
from .models import *
class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self,request,view,obj):

        if(request.method in permissions.SAFE_METHODS and obj is not None ):
            return True
        
        return str(obj.username) == str(request.user)

class IsSelf(permissions.BasePermission):

    def has_object_permission(self,request,view,obj):

        if(request.method in permissions.SAFE_METHODS and obj is not None ):
            return True

        if(isinstance(obj,Vehicle)):
            return str(obj.employee.user.username) == str(request.user)
        
        elif(isinstance(obj,Employee) or isinstance(obj,EmployeeOfficial)):
            return str(obj.user.username) == str(request.user)

        
