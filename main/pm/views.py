from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Property, Lease, Problem
from .forms import NewPropertyForm, NewLeaseForm, NewProblemForm

# Create your views here.
@login_required
def home(request):
    return render(request, 'pm/home.html', {})

@login_required
def create_property(request):
    if request.method == 'POST':
        form = NewPropertyForm(request.POST)
        if form.is_valid():
            property = form.save(commit=False)
            property.owner = request.user
            property.save()
            messages.success(request, 'Property created successfully!')
            return redirect('pm:home')
    else:
        form = NewPropertyForm()
    return render(request, 'pm/create_property.html', {'form': form})

@login_required
def create_lease(request):
    if request.method == 'POST':
        form = NewLeaseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lease created successfully!')
            return redirect('pm:home')
    else:
        form = NewLeaseForm()
    return render(request, 'pm/create_lease.html', {'form': form})

@login_required
def report_problem(request):
    if request.method == 'POST':
        form = NewProblemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Problem reported successfully!')
            return redirect('pm:home')
    else:
        form = NewProblemForm()
    return render(request, 'pm/report_problem.html', {'form': form})