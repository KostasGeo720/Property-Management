from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create_property', views.create_property, name='create_property'),
    path('create_lease/<int:property_id>/', views.create_lease, name='create_lease'),
    path('edit_lease/<int:property_id>/', views.edit_lease, name='edit_lease'),
    path('report_problem', views.report_problem, name='report_problem'),
    path('solve_problem/<int:problem_id>/', views.solve_problem, name='solve_problem'),
    path('manage_properties/', views.manage_properties, name='manage_properties'),
    path('add_tennant/<int:property_id>/', views.add_tennant, name='add_tennant'),
    path('remove_tennant/<int:lease_id>/<int:tennant_id>/', views.remove_tennant, name='remove_tennant'),
    path('edit_property/<int:property_id>/', views.edit_property, name='edit_property'),
    path('delete_property/<int:property_id>/', views.delete_property, name='delete_property'),
    path('delete_lease/<int:lease_id>/', views.delete_lease, name='delete_lease'),
    path('payment_status/<int:lease_id>/', views.payment_status, name='payment_status'),
]

