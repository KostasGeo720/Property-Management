from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm

# Create your views here.
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, 'Έχετε συνδεθεί επιτυχώς!')
            return redirect('home')
        else:
            messages.error(request, 'Το όνομα χρήστη ή ο κωδικός πρόσβασής σας είναι λανθασμένος.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout(request):
    auth_logout(request)
    messages.success(request, 'Έχετε αποσυνδεθεί επιτυχώς!')
    return redirect('login')