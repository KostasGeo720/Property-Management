from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.tenant_signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('owner_signup/', views.owner_signup, name='owner_signup'),
]
