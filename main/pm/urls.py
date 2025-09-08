from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create_property', views.create_property, name='create_property'),
    path('create_lease', views.create_lease, name='create_lease'),
    path('report_problem', views.report_problem, name='report_problem'),
    path('solve_problem/<int:problem_id>/', views.solve_problem, name='solve_problem'),
    path('manage_properties/', views.manage_properties, name='manage_properties'),
    path('status_price/<int:property_id>/', views.status_price, name='status_price'),
    path('status_rent/<int:property_id>/', views.status_rent, name='status_rent'),
]
