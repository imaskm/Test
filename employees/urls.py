from django.urls import path
from django.conf.urls import include,url
from .views import *
'''
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
'''
urlpatterns= [    
    url(r'^api-auth/',include('rest_framework.urls')),
    url(r'^$',APIRoot.as_view(),name='api_root'),
    url(r'^user/(?P<pk>\d+)/$',UserDetails.as_view(),name='user_details'),
    url(r'^users/$',EmployeeDetails.as_view(),name='employee_details'),
    url(r'^user/(?P<pk>\d+)/personalinfo/$',EmployeeInfo.as_view(),name='employee-details' ),
    url(r'^users/vehicles/(?P<pk>\d+)/$',VehicleInfo.as_view(),name='vehicle-details' ),
    url(r'^users/vehicles/(?P<pk>\d+)/add/$',VehicleAdd.as_view(),name='vehicle_add' ),
    url(r'^vehicles/$', VehicleList.as_view(),name= 'vehicle_list'  ),
    url(r'^user/(?P<pk>\d+)/officialinfo/$',EmployeeOfficialInfo.as_view(),name='employeeofficial-details'),
    url(r'^search/$',SearchList.as_view(),name='search' ),
    url(r'^searchall/(?P<query>\w*)/$',GenericSearch.as_view(),name='generic_search' ),

]
   

'''urlpatterns += patterns('',
   url(r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),)
urlpatterns += staticfiles_urlpatterns()'''
