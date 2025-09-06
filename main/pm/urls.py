from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create_property', views.create_property, name='create_property'),
    path('create_lease', views.create_lease, name='create_lease'),
    path('report_problem', views.report_problem, name='report_problem'),
]
