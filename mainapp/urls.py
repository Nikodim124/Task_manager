from django.urls import path
from .views import *


urlpatterns = [
    path('', project_list, name='project_list'),
    path('project_list_all', project_list_all, name='project_list_all'),
    path('create', project_create, name='project_create'),
    path('projects/<pk>/details', project_details, name='project_details'),
    path('delete_projects/<pk>', project_delete, name='project_delete'),
    path('archive', send_to_archive, name='send_to_archive'),

    path('employees', emp_view, name='employees'),
    path('employees/<pk>/details', emp_details, name='emp_details'),

    path('customers', cust_view, name='customers'),
    path('customers/<pk>/details', customer_details, name='customer_details'),
    path('new_customer', add_customer, name='add_customer'),

    path('contracts', contract_view, name='contracts'),

    path('my_projects', my_projects, name='my_projects'),

    path('oops', error_view, name='error'),

    path('login', login_view, name='login'),
    path('create_tasks/', create_tasks, name='create_tasks'),
    path('validate_status', validate_status, name='validate_status'),

    path('pdf_view/', ViewPDF.as_view(), name="pdf_view"),

    path('search', search, name='search'),

    path('stats', stats_view, name='stats'),
    path('stats_data', stats_data, name='stats_data'),
]
