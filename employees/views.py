from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.http import Http404
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status,permissions,filters
from rest_framework.decorators import api_view
import copy
from django.contrib.auth.models import User
from employees.models import *
from rest_framework.views import APIView
from employees.serializers import *
from .permissions import IsOwnerOrReadOnly,IsSelf
from rest_framework import generics
from django.db.models import Q
from itertools import chain
from django.http import HttpResponseRedirect
from rest_framework.pagination import PageNumberPagination
from .pagination import CustomPagination
from django_filters.rest_framework import DjangoFilterBackend


def get_model_fields(model):
    
    return list( field.name for field in model._meta.fields )

class VehicleInfo(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = (permissions.IsAuthenticated,IsSelf )
    
    def delete(self,request,*args,**kwargs):
        super().delete(request,**kwargs)
        print(vars(request))
        
        return HttpResponseRedirect( reverse('employee-details', kwargs={"pk":request.user.id})  )

class VehicleAdd(generics.CreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = (permissions.IsAuthenticated,IsSelf )
    
    
    def post(self,request,*args,**kwargs):
        super().post(request,**kwargs)
        return HttpResponseRedirect( reverse('employee-details', request=request, kwargs={"pk":request.user.id})  )

class VehicleList(generics.ListAPIView):
    queryset           = Vehicle.objects.all()
    serializer_class   = VehicleSerializer
    permission_classes = (permissions.IsAuthenticated,IsSelf)
    pagination_class   = CustomPagination
    filter_backends    = (filters.SearchFilter,filters.OrderingFilter,)
    search_fields      = ('vehicle_number','vehicle_type')   
    ordering_fields    = ('vehicle_type',)


class EmployeeInfo(generics.RetrieveUpdateAPIView,generics.CreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeListSerializer
    permission_classes=(permissions.IsAuthenticated,IsSelf )
    
    
class EmployeeOfficialInfo(generics.RetrieveUpdateAPIView,generics.CreateAPIView):
    queryset = EmployeeOfficial.objects.filter(is_current_employee=True)
    serializer_class = EmployeeOfficialSerializer
    permission_classes=(permissions.IsAuthenticated,IsSelf )

class EmployeeDetails( generics.ListAPIView  ):
    queryset = User.objects.filter(is_active=True)
    permission_classes=(permissions.IsAuthenticated, )
    serializer_class = UserListSerializer
    filter_backends = (filters.SearchFilter,filters.OrderingFilter,)
    search_fields = ( 'username',
                      'email',
                      'personal_data__mobile',
                      'first_name',
                      'last_name' ,
                      'personal_data__mobile_emergency',
                      'official_data__skills')
    ordering_fields = ('username',)
    pagination_class   = CustomPagination

class UserDetails(generics.RetrieveUpdateAPIView):
    
    serializer_class   = UserListSerializer     
    queryset = User.objects.filter(is_active=True)
    permission_classes=(permissions.IsAuthenticated,IsOwnerOrReadOnly, )
    pagination_class   = CustomPagination
    
class APIRoot(generics.ListAPIView):
    
    permission_classes=(permissions.IsAuthenticated, )

    def get(self,request):

        return Response({
        'View My Details'     : reverse('user_details', request=request, kwargs={'pk':request.user.id}),
        'View All Employees'  : reverse('employee_details', request=request),
        'Generic Search'      : reverse('generic_search',request=request,kwargs={'query':''}),
        'View All Vehicles'   : reverse('vehicle_list',request=request),
        'Parametric Search'   : reverse('search',request=request)
        

        })

class SearchList(generics.ListAPIView):
    permission_classes=(permissions.IsAuthenticated, )
    serializer_class  = UserListSerializer
 
    def get_queryset(self):
        
        query_dict  = dict(self.request.query_params)
        print("QueryDict" , query_dict) 
        if(query_dict == None or query_dict == {} ):
            print("Here")    
            return []  
        
        user_fields = get_model_fields(User)
        employee_official_fields = get_model_fields(EmployeeOfficial)
        employee_fields  = get_model_fields(Employee)
        vehicle_fields = get_model_fields(Vehicle)
        

        #Fetching User Data 
        q_user=Q()
        q_employee_official =Q()
        q_employee = Q()
        q_vehicle = Q()

        flag_user = False
        flag_employee_official =False
        flag_employee  = False
        flag_vehicle = False
        for key in query_dict.keys():
                            
            if( key in user_fields):
                flag_user =True
                flag_u = 1
                for value in query_dict[key]:
                    if(flag_u == 1):
                        q_user|=Q(**{ '%s__icontains'%key:value } )
                        flag_u+=1
                    else:
                        q_user|=Q(**{ '%s__icontains'%key:value } )
            
            elif( key in employee_official_fields  ):
                flag_employee_official =True
                flag_eo = 1

                for value in query_dict[key]:
                    if(flag_eo == 1 ):
                        
                        if(key == 'manager'):
                            q_employee_official|=Q(**{ '%s__username__icontains'%key:value } )
                        else:
                            q_employee_official|=Q(**{ '%s__icontains'%key:value } )
                        flag_eo+= 1
                    else:
                        if(key == "manager" ):
                            q_employee_official|=Q(**{ '%s__username__icontains'%key:value  } )
                        else:
                            q_employee_official|=Q(**{ '%s__icontains'%key:value  } )
            
            elif( key in employee_fields  ) :
                flag_employee = True
                flag_e = 1
                for value in query_dict[key]:
                    if(flag_e == 1 ):
                        q_employee|=Q(**{ '%s__icontains'%key:value } )
                        flag_e+=1
                    else:
                        q_employee|=Q(**{ '%s__icontains'%key:value  } )

            elif( key in vehicle_fields  ):
                flag_vehicle = True
                flag_v  =  1
                for value in query_dict[key]:
                    if(flag_v == 1 ):
                        q_vehicle|=Q(**{ '%s__icontains'%key:value } )
                        flag_v+=1
                    else:
                        q_vehicle|=Q(**{ '%s__icontains'%key:value } )

        users = []
        if(flag_user == True ):
            users = list(User.objects.filter( q_user ) )
        
        employee_officials = []
        if(flag_employee_official == True ):
            employee_officials = list(EmployeeOfficial.objects.filter( q_employee_official) )
        
        employees = []
        if(flag_employee == True ):
            employees = list(Employee.objects.filter( q_employee) )
        
        vehicles = []
        if(flag_vehicle == True ):
            vehicles = list(Vehicle.objects.filter(q_vehicle ) )

        user_ids = []

        for user in users:
            user_ids.append(user.id)

        for employee in employee_officials:
            user_ids.append(employee.user.id)
        
        for employee in employees:
            user_ids.append(employee.user.id)

        for vehicle in vehicles:
            user_ids.append(vehicle.employee.user.id)

        user_ids = list(set(user_ids))

        users = User.objects.filter( id__in =  user_ids ).filter(is_active = True)

        return users


class GenericSearch(generics.ListAPIView):

    permission_classes=(permissions.IsAuthenticated, )
    serializer_class  = UserListSerializer
 
    def get_queryset(self):
        
        query = self.kwargs.get('query',None)
        
        if(query == None or query == '' ):
            return [] 
        

        users = list(User.objects.filter( Q(username__icontains   = query ) | 
                                          Q(first_name__icontains = query ) |
                                          Q(last_name__icontains  = query ) |
                                          Q(email__icontains      = query)
                                     
                                        ) 
                     )
        employee_officials = list(EmployeeOfficial.objects.filter(  Q(team__icontains          = query ) |
                                                                    Q(designation__icontains   = query ) |
                                                                    Q(skills__icontains        = query ) 
                                                                 ) 
                                 )
        if(query.isdigit() ):


            employees  = list( Employee.objects.filter( Q(mobile__icontains        = query ) |
                                                    Q(email_alternate__icontains   = query ) |
                                                    Q(mobile_emergency__icontains  = query ) |
                                                    Q(address__icontains           = query ) 
                                                  )
                         )
        
        else:
            employees  = list( Employee.objects.filter( Q(email_alternate__icontains   = query ) |
                                                        Q(address__icontains           = query ) |
                                                        Q(blood_group__icontains       = query )
                                                     )
                             )

        
       
        vehicles = list( Vehicle.objects.filter( Q( vehicle_number__icontains   = query ) |
                                                 Q( vehicle_type__icontains     = query )
                                                     )
                             )

        user_ids = []

        for user in users:
            user_ids.append(user.id)

        for employee in employee_officials:
            user_ids.append(employee.user.id)
        
        for employee in employees:
            user_ids.append(employee.user.id)

        for vehicle in vehicles:
            user_ids.append(vehicle.employee.user.id)
        
        user_ids = list(set(user_ids))
        users = User.objects.filter( id__in =  user_ids )

        return users

