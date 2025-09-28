from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import NewUserForm

# Create your views here.
def tenant_signup(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created! You can now login.')
            return redirect('login')
        else:
            messages.error(request, 'Your form is not valid. Please correct the errors.')
    else:
        form = NewUserForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, 'You have been logged in!')
            return redirect('home')
        else:
            messages.error(request, 'Your username or password is incorrect.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out!')
    return redirect('login')

def owner_signup(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_staff = True  # Mark user as staff (owner)
            user.save()
            messages.success(request, 'Your owner account has been created! You can now login.')
            return redirect('login')
        else:
            messages.error(request, 'Your form is not valid. Please correct the errors.')
    else:
        form = NewUserForm()
    return render(request, 'accounts/owner_signup.html', {'form': form})