from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('new_property_page', views.new_property_page, name='new_property_page'),
    path('create_property_complex', views.create_property_complex, name='create_property_complex'),
    path('add_property_to_complex/<str:address>/', views.create_unit, name='add_property_to_complex'),
    path('create_property', views.create_property, name='create_property'),
    path('create_lease/<uuid:property_id>/', views.create_lease, name='create_lease'),
    path('create_lease_unit/<uuid:unit_id>/', views.create_lease_unit, name='create_lease_unit'),
    path('edit_lease/<uuid:property_id>/', views.edit_lease, name='edit_lease'),
    path('edit_lease_unit/<uuid:unit_id>/', views.edit_lease_unit, name='edit_lease_unit'),
    path('report_problem', views.report_problem, name='report_problem'),
    path('solve_problem/<int:problem_id>/', views.solve_problem, name='solve_problem'),
    path('manage_properties/', views.manage_properties, name='manage_properties'),
    path('add_tennant/<uuid:property_id>/', views.add_tennant, name='add_tennant'),
    path('remove_tennant/<uuid:lease_id>/<uuid:tennant_id>/', views.remove_tennant, name='remove_tennant'),
    path('edit_property/<uuid:property_id>/', views.edit_property, name='edit_property'),
    path('manage_unit/<uuid:unit_id>/', views.manage_unit, name='manage_unit'),
    path('delete_property/<uuid:property_id>/', views.delete_property, name='delete_property'),
    path('delete_complex/<uuid:complex_id>/', views.delete_complex, name='delete_complex'),
    path('delete_unit/<uuid:unit_id>/', views.delete_unit, name='delete_unit'),
    path('delete_lease/<uuid:lease_id>/', views.delete_lease, name='delete_lease'),
    path('payment_status/<uuid:lease_id>/', views.payment_status, name='payment_status'),
    path('finances/', views.finances, name='finances'),
    path('submit_payment/<uuid:lease_id>/', views.submit_payment, name='submit_payment'),
    path('documents/', views.documents, name='documents'),
]

