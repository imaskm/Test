from rest_framework import serializers
from django.contrib.auth.models import User
from employees.models import Employee,EmployeeOfficial,Vehicle
from rest_framework.reverse import reverse
from rest_framework.response import Response
from django.db import IntegrityError
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models import Q
from collections import OrderedDict
import re

class VehicleSerializer(serializers.ModelSerializer ):

    id = serializers.IntegerField(required=False)
    employee = serializers.SerializerMethodField()
    class Meta:
        model   = Vehicle
        fields  = ('id','vehicle_number','vehicle_type','employee',)
        read_only_fields = ('employee',)
        extra_kwargs = {
            'vehicle_number': {
                'validators': [],
            }} 

    '''def get_fields(self,*args):

        fields = super().get_fields()
        
        print(type(self.instance))
        if(self.instance is not None and (str(self.instance.employee.user.username) == str(self._context['request'].user)) ):

            fields.pop("employee")

        return fields'''


    def validate_vehicle_number(self,vehicle_number):
        
        if(re.search(r'^[a-zA-Z]{2}[0-9]{1,2}[a-zA-Z]{1,2}[0-9]{4}$',vehicle_number) ):
            return vehicle_number

        else:
            raise serializers.ValidationError('Vehicle number is not valid')

    def validate(self,vehicles):
        
        vehicle_id = vehicles.get("id",0)
        vehicle_number = vehicles.get("vehicle_number",None)
        vehicle_type   = vehicles.get("vehicle_type",None)
        
        if(vehicle_number is None ):
            raise serializers.ValidationError('Vehicle number can not be blank')

        if(vehicle_type is None ):
            raise serializers.ValidationError('Vehicle Type can not be blank')

        if( vehicle_id == 0):
                
            try:
                    
                vehicle_obj = Vehicle.objects.get(vehicle_number = vehicle_number)
                     
                if(vehicle_obj.employee.user.username == self.context['request'].user):
                    raise serializers.ValidationError('This vehicle is already registered by you')
                else:
                    raise serializers.ValidationError('Vehicle number ( %s  ) already exists for employee %s'
                                                     %(vehicle_obj.vehicle_number,vehicle_obj.employee.employee_id)  )                    
            except Vehicle.DoesNotExist:
                pass
        else:
            vehicle_obj = None

            try:

                vehicle_obj = Vehicle.objects.get( ~Q(id = vehicle_id), Q(vehicle_number=vehicle_number))

                if(vehicle_obj.employee.user.username == self._args[0].user.username):
                    raise serializers.ValidationError('Two vehicles can not have same registeration number')

                else:

                    raise serializers.ValidationError('Vehicle number ( %s  ) already exists for employee %s'
                                                      %(vehicle_obj.vehicle_number,vehicle_obj.employee.employee_id)  )
                    
            except Vehicle.DoesNotExist:
                pass

        return vehicles


    def create(self,validated_data) :
        
        try:

            vehicle_obj= Vehicle.objects.create(vehicle_type   = validated_data["vehicle_type"],
                                                vehicle_number = validated_data["vehicle_number"],
                                                employee       = Employee.objects.get(user = self.context['request'].user))
            return vehicle_obj

        
        except:
            raise serializers.ValidationError('Vehicle Already Exists')


    def get_employee(self,obj):

        if(obj is not None ):

            return reverse('user_details', request = self.context['request'], kwargs={'pk':obj.employee.user.id})

            return obj.employee.employee_id
        else:
            return None

class EmployeeOfficialSerializer(serializers.ModelSerializer):
    
    manager_details =  serializers.SerializerMethodField()
    
    class Meta:
        model            = EmployeeOfficial
        #fields           = '__all__'
        exclude          = ('user','is_current_employee',)
        read_only_fields = ('employee_id',)
    
    def get_fields(self,*args):

        fields = super().get_fields()

        if(self.instance is not None and (str(self.instance.user.username) != str(self._context['request'].user)) ):

            fields.pop("manager")

        return fields

    def create(self,validated_data):
        
        user = self._context['request'].user
        validated_data['user'] = user
        employee_id = user.username
        validated_data['employee_id'] = employee_id
            
        try:    
            emp_obj = EmployeeOfficial.objects.create(**validated_data)
            
            return emp_obj
        
        except IntegrityError as e:
            
            raise serializers.ValidationError("Post request not allowed for existing data")
        
        except :          
            raise serializers.ValidationError('Error Ocurred in processing....')



    def get_manager_details(self,obj):
        
        try:
            if(obj.manager is not None): 

                return reverse('user_details', request = self.context['request'], kwargs={'pk':obj.manager.id})

            else:
                return None
        except :
            return None

    
class EmployeeListSerializer(serializers.HyperlinkedModelSerializer ):

    vehicles = serializers.HyperlinkedIdentityField(view_name = 'vehicle-details',read_only=True,required=False,many=True )    
    add_vehicle = serializers.SerializerMethodField()

    class Meta:
        model  = Employee
        fields = ('mobile','email_alternate','mobile_emergency','address','blood_group','vehicles','add_vehicle',)
        #exclude  = ('employee_id','user',)
    
    def create(self,validated_data):
        
        user = self._context['request'].user
        validated_data['user'] = user
        
        try:
            emp_obj = Employee.objects.create(**validated_data)
            return emp_obj
        except IntegrityError:
            raise serializers.ValidationError('Post request not allowed')
        except : 
            raise serializers.ValidationError('Error Ocurred in processing....')
        
    #to hide blank field , we can use this    
    '''def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Here we filter the null values and creates a new dictionary
        # We use OrderedDict like in original method
        ret = OrderedDict(list(filter(lambda x: x[1], ret.items())))
        return ret'''

    def get_fields(self,*args):

        fields = super().get_fields()
        
        if( self.instance is not None and ( str(self.instance.user.username) != str(self._context['request'].user) ) ):
        
            fields.pop("add_vehicle") 
        
        return fields
    
    def get_add_vehicle(self,obj):

        try:
            if(obj is not None):

                return reverse('vehicle_add', request = self.context['request'], kwargs={'pk':obj.user.id})

            else:
                return None
        except :
            return None

    def validate(self,data):

        if(data['mobile'] == data['mobile_emergency'] and data['mobile'] is not None and data['mobile_emergency'] is not None):
            raise serializers.ValidationError('Mobile and Emergency Mobile Number should be different')
        else:
            return data
    
    def validate_mobile(self,mobile):

        if(len(str(mobile)) != 10  and mobile is not None):
            raise serializers.ValidationError('Mobile number must contain 10 digits')
        else:
            return mobile
    
    def validate_mobile_emergency(self,mobile):
        
        if(len(str(mobile)) != 10 and mobile is not None ):
            raise serializers.ValidationError('Emergency Mobile number must contain 10 digits')
        else:
            return mobile

class UserListSerializer(serializers.HyperlinkedModelSerializer ):
    
    personal_data = serializers.HyperlinkedIdentityField(view_name = 'employee-details',read_only=True )

    official_data = serializers.HyperlinkedIdentityField(view_name = 'employeeofficial-details',read_only=True )

    class Meta:
        model  = User
        fields = ('username','first_name','last_name','email','personal_data','official_data',)
        #exclude  = ('employee_id','user',)
        read_only_fields = ('username','email',)
        
